# -*- coding: utf-8 -*-
"""
SpaceMouse Navigation Plugin for QGIS
"""

from qgis.PyQt.QtCore import QTimer, QThread, pyqtSignal, QSettings
from qgis.PyQt.QtWidgets import QAction, QMessageBox
from qgis.PyQt.QtGui import QIcon
from qgis.core import QgsPointXY
import os

from .settings_dialog import SpaceMouseSettingsDialog

# Try to import HID library
SPACEMOUSE_AVAILABLE = False
HID_ERROR = None
try:
    import hid
    SPACEMOUSE_AVAILABLE = True
except ImportError as e:
    HID_ERROR = str(e)
    # Try alternative hidapi package
    try:
        import hidapi as hid
        SPACEMOUSE_AVAILABLE = True
        HID_ERROR = None
    except ImportError as e2:
        HID_ERROR = f"hid: {e}\nhidapi: {e2}"


class SpaceMouseThread(QThread):
    """Background thread to read SpaceMouse data"""
    movement_signal = pyqtSignal(float, float, float)
    error_signal = pyqtSignal(str)
    
    # 3Dconnexion vendor IDs
    VENDOR_IDS = [
        0x256f,  # 3Dconnexion (newer devices)
        0x046d,  # Logitech/3Dconnexion (older devices)
    ]
    
    # Known SpaceMouse product IDs
    PRODUCT_IDS = [
        # 3Dconnexion (0x256f) devices
        0xc62e, 0xc62f, 0xc631, 0xc632, 0xc633, 0xc635, 0xc636, 0xc640,
        # Logitech/3Dconnexion (0x046d) devices  
        0xc603, 0xc605, 0xc606, 0xc621, 0xc623, 0xc625, 0xc626, 0xc627,
        0xc628, 0xc629, 0xc62b, 0xc62e, 0xc62f, 0xc631, 0xc632, 0xc633,
    ]
    
    def __init__(self):
        super().__init__()
        self.running = False
        self.device = None
        
    def run(self):
        """Main thread loop"""
        self.running = True
        
        try:
            # Find SpaceMouse device by checking product names
            all_devices = hid.enumerate()
            
            spacemouse_device = None
            for device_info in all_devices:
                product = device_info.get('product_string', '').lower()
                manufacturer = device_info.get('manufacturer_string', '').lower()
                vid = device_info['vendor_id']
                pid = device_info['product_id']
                
                # Check if it's a 3Dconnexion device
                is_3dconnexion = (
                    '3dconnex' in manufacturer or
                    'space' in product or
                    (vid in self.VENDOR_IDS and pid in self.PRODUCT_IDS)
                )
                
                if is_3dconnexion:
                    spacemouse_device = device_info
                    print(f"Found SpaceMouse: {device_info.get('product_string', 'Unknown')}")
                    print(f"  Manufacturer: {device_info.get('manufacturer_string', 'Unknown')}")
                    print(f"  VID: 0x{vid:04x}, PID: 0x{pid:04x}")
                    break
            
            if not spacemouse_device:
                self.error_signal.emit("No SpaceMouse device found. Make sure it's plugged in.")
                return
            
            device_info = spacemouse_device
            product_name = device_info.get('product_string', 'Unknown')
            
            print(f"Opening SpaceMouse: {product_name}")
            print(f"  VID: 0x{device_info['vendor_id']:04x}")
            print(f"  PID: 0x{device_info['product_id']:04x}")
            
            # Open the device using hid.device() syntax
            self.device = hid.device()
            self.device.open(device_info['vendor_id'], device_info['product_id'])
            self.device.set_nonblocking(1)
            
            print("SpaceMouse opened successfully, starting read loop...")
            
            # Read loop
            read_count = 0
            while self.running:
                try:
                    data = self.device.read(64)
                    
                    if data and len(data) > 0:
                        read_count += 1
                        
                        # Debug: print first few packets
                        if read_count <= 3:
                            print(f"Packet {read_count}: {list(data[:8])}")
                        
                        # Parse the data
                        x, y, z = self._parse_spacemouse_data(data)
                        
                        # Only emit if there's actual movement
                        if abs(x) > 0.001 or abs(y) > 0.001 or abs(z) > 0.001:
                            self.movement_signal.emit(x, y, z)
                    
                    # Small sleep to prevent CPU spinning
                    import time
                    time.sleep(0.01)
                    
                except Exception as e:
                    print(f"Read error: {e}")
                    break
            
            print(f"SpaceMouse thread stopped. Total packets: {read_count}")
                    
        except Exception as e:
            error_msg = f"SpaceMouse error: {e}"
            print(error_msg)
            self.error_signal.emit(error_msg)
        finally:
            if self.device:
                try:
                    self.device.close()
                    print("SpaceMouse device closed")
                except:
                    pass
    
    def _parse_spacemouse_data(self, data):
        """Parse raw HID data from SpaceMouse
        
        SpaceMouse Compact format:
        Report ID 1: Translation (X, Y, Z)
        Report ID 2: Rotation (Roll, Pitch, Yaw) - we ignore this for 2D navigation
        Report ID 3: Buttons (if present)
        """
        if len(data) < 7:
            return 0.0, 0.0, 0.0
        
        # Report ID in data[0] tells us what type of data this is
        report_id = data[0]
        
        # We only care about Report ID 1 (translation)
        if report_id != 1:
            return 0.0, 0.0, 0.0
        
        def bytes_to_int16(low, high):
            """Convert two bytes to signed 16-bit integer"""
            value = (high << 8) | low
            if value >= 32768:
                value -= 65536
            return value / 350.0  # Scale to approximately -1.0 to 1.0
        
        # Translation data for Report ID 1:
        # Bytes 1-2: X axis (left/right)
        # Bytes 3-4: Y axis (forward/back)
        # Bytes 5-6: Z axis (up/down)
        x = bytes_to_int16(data[1], data[2])
        y = bytes_to_int16(data[3], data[4])
        z = bytes_to_int16(data[5], data[6])
        
        return x, y, z
    
    def stop(self):
        """Stop the thread"""
        print("Stopping SpaceMouse thread...")
        self.running = False
        self.wait()


class SpaceMousePlugin:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor."""
        self.iface = iface
        self.canvas = iface.mapCanvas()
        self.action = None
        self.settings_action = None
        self.thread = None
        self.enabled = False
        
        # QSettings for persistent storage
        self.qsettings = QSettings()
        
        # Load settings
        self.load_settings()

    def load_settings(self):
        """Load settings from QSettings"""
        self.settings = {
            'invert_x': self.qsettings.value('spacemouse/invert_x', False, type=bool),
            'invert_y': self.qsettings.value('spacemouse/invert_y', False, type=bool),
            'invert_z': self.qsettings.value('spacemouse/invert_z', False, type=bool),
            'swap_yz': self.qsettings.value('spacemouse/swap_yz', True, type=bool),
            'pan_sensitivity': self.qsettings.value('spacemouse/pan_sensitivity', 0.005, type=float),
            'zoom_sensitivity': self.qsettings.value('spacemouse/zoom_sensitivity', 0.01, type=float),
            'deadzone': self.qsettings.value('spacemouse/deadzone', 0.05, type=float),
        }
    
    def save_settings(self):
        """Save settings to QSettings"""
        self.qsettings.setValue('spacemouse/invert_x', self.settings['invert_x'])
        self.qsettings.setValue('spacemouse/invert_y', self.settings['invert_y'])
        self.qsettings.setValue('spacemouse/invert_z', self.settings['invert_z'])
        self.qsettings.setValue('spacemouse/swap_yz', self.settings['swap_yz'])
        self.qsettings.setValue('spacemouse/pan_sensitivity', self.settings['pan_sensitivity'])
        self.qsettings.setValue('spacemouse/zoom_sensitivity', self.settings['zoom_sensitivity'])
        self.qsettings.setValue('spacemouse/deadzone', self.settings['deadzone'])

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        
        icon_path = os.path.join(os.path.dirname(__file__), 'icon.png')
        
        # Enable/Disable action
        self.action = QAction(
            QIcon(icon_path) if os.path.exists(icon_path) else QIcon(),
            "Enable SpaceMouse",
            self.iface.mainWindow()
        )
        self.action.setCheckable(True)
        self.action.setChecked(False)
        self.action.triggered.connect(self.toggle_spacemouse)
        
        # Settings action
        self.settings_action = QAction(
            "SpaceMouse Settings",
            self.iface.mainWindow()
        )
        self.settings_action.triggered.connect(self.show_settings)
        
        # Add toolbar button and menu items
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu("&SpaceMouse Navigation", self.action)
        self.iface.addPluginToMenu("&SpaceMouse Navigation", self.settings_action)
        
        # Check if hid library is available
        if not SPACEMOUSE_AVAILABLE:
            self.action.setEnabled(False)
            self.settings_action.setEnabled(False)
            error_msg = "HID library not found.\n\n"
            error_msg += "Please install using OSGeo4W Shell:\n"
            error_msg += "python -m pip install hidapi\n\n"
            if HID_ERROR:
                error_msg += f"Error details:\n{HID_ERROR}"
            QMessageBox.warning(
                self.iface.mainWindow(),
                "SpaceMouse Plugin",
                error_msg
            )

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        if self.enabled:
            self.stop_spacemouse()
            
        self.iface.removePluginMenu("&SpaceMouse Navigation", self.action)
        self.iface.removePluginMenu("&SpaceMouse Navigation", self.settings_action)
        self.iface.removeToolBarIcon(self.action)

    def toggle_spacemouse(self, checked):
        """Enable or disable SpaceMouse navigation"""
        if checked:
            self.start_spacemouse()
        else:
            self.stop_spacemouse()
    
    def show_settings(self):
        """Show the settings dialog"""
        dialog = SpaceMouseSettingsDialog(self.iface.mainWindow())
        dialog.set_settings(self.settings)
        
        if dialog.exec_():
            self.settings = dialog.get_settings()
            self.save_settings()
            self.iface.messageBar().pushMessage(
                "SpaceMouse",
                "Settings saved",
                level=0,
                duration=2
            )

    def start_spacemouse(self):
        """Start reading from SpaceMouse"""
        if not SPACEMOUSE_AVAILABLE:
            return
            
        if self.thread is None or not self.thread.isRunning():
            self.thread = SpaceMouseThread()
            self.thread.movement_signal.connect(self.handle_movement)
            self.thread.error_signal.connect(self.handle_error)
            self.thread.start()
            self.enabled = True
            self.iface.messageBar().pushMessage(
                "SpaceMouse", 
                "SpaceMouse navigation enabled - check Python Console for details", 
                level=0,
                duration=3
            )

    def stop_spacemouse(self):
        """Stop reading from SpaceMouse"""
        if self.thread and self.thread.isRunning():
            self.thread.stop()
            self.thread = None
            self.enabled = False
            self.iface.messageBar().pushMessage(
                "SpaceMouse",
                "SpaceMouse navigation disabled",
                level=0,
                duration=3
            )
    
    def handle_error(self, error_msg):
        """Handle errors from the SpaceMouse thread"""
        self.iface.messageBar().pushMessage(
            "SpaceMouse Error",
            error_msg,
            level=2,
            duration=5
        )
        self.action.setChecked(False)
        self.enabled = False

    def handle_movement(self, x, y, z):
        """Handle SpaceMouse movement data
        
        :param x: Left/right movement (-1.0 to 1.0)
        :param y: Forward/back movement (-1.0 to 1.0)
        :param z: Up/down movement (-1.0 to 1.0)
        """
        
        # Apply inversions
        if self.settings['invert_x']:
            x = -x
        if self.settings['invert_y']:
            y = -y
        if self.settings['invert_z']:
            z = -z
        
        # Apply deadzone
        deadzone = self.settings['deadzone']
        if abs(x) < deadzone:
            x = 0
        if abs(y) < deadzone:
            y = 0
        if abs(z) < deadzone:
            z = 0
        
        # Skip if no movement
        if x == 0 and y == 0 and z == 0:
            return
        
        # Swap Y and Z if configured
        if self.settings['swap_yz']:
            y, z = z, y
        
        # Get current map extent
        extent = self.canvas.extent()
        width = extent.width()
        height = extent.height()
        
        # Calculate pan distances
        pan_x = x * width * self.settings['pan_sensitivity']
        pan_y = -y * height * self.settings['pan_sensitivity']  # Negative for correct direction
        
        # Get current center and calculate new center
        center = self.canvas.center()
        new_center = QgsPointXY(
            center.x() + pan_x,
            center.y() + pan_y
        )
        
        # Apply panning if there's pan movement
        if pan_x != 0 or pan_y != 0:
            self.canvas.setCenter(new_center)
        
        # Apply zoom
        if z != 0:
            zoom_factor = 1.0 - (z * self.settings['zoom_sensitivity'])
            self.canvas.zoomByFactor(zoom_factor)
        
        # Refresh the canvas
        self.canvas.refresh()
