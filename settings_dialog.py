# -*- coding: utf-8 -*-
"""
Settings dialog for SpaceMouse Plugin
"""

from qgis.PyQt.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QGroupBox,
                                  QCheckBox, QLabel, QDoubleSpinBox, QPushButton,
                                  QDialogButtonBox)
from qgis.PyQt.QtCore import Qt


class SpaceMouseSettingsDialog(QDialog):
    """Settings dialog for configuring SpaceMouse behavior"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("SpaceMouse Settings")
        self.setMinimumWidth(400)
        
        # Default settings
        self.settings = {
            'invert_x': False,
            'invert_y': False,
            'invert_z': False,
            'swap_yz': True,  # Default to swapped (forward/back for pan, up/down for zoom)
            'pan_sensitivity': 0.005,
            'zoom_sensitivity': 0.01,
            'deadzone': 0.05
        }
        
        self.setup_ui()
    
    def setup_ui(self):
        """Create the UI elements"""
        layout = QVBoxLayout()
        
        # Axis Configuration Group
        axis_group = QGroupBox("Axis Configuration")
        axis_layout = QVBoxLayout()
        
        # Invert checkboxes
        self.invert_x_cb = QCheckBox("Invert Left/Right (X axis)")
        self.invert_y_cb = QCheckBox("Invert Forward/Back (Y axis)")
        self.invert_z_cb = QCheckBox("Invert Up/Down (Z axis)")
        
        axis_layout.addWidget(self.invert_x_cb)
        axis_layout.addWidget(self.invert_y_cb)
        axis_layout.addWidget(self.invert_z_cb)
        
        # Swap Y/Z checkbox
        axis_layout.addWidget(QLabel(""))  # Spacer
        self.swap_yz_cb = QCheckBox("Swap Y/Z axes (Forward/Back ↔ Up/Down)")
        self.swap_yz_cb.setChecked(True)  # Default checked
        axis_layout.addWidget(self.swap_yz_cb)
        
        # Add explanation label
        self.axis_explanation = QLabel()
        self.axis_explanation.setWordWrap(True)
        self.axis_explanation.setStyleSheet("QLabel { color: gray; font-size: 9pt; }")
        axis_layout.addWidget(self.axis_explanation)
        self.update_axis_explanation()
        
        # Connect to update explanation when swap changes
        self.swap_yz_cb.stateChanged.connect(self.update_axis_explanation)
        
        axis_group.setLayout(axis_layout)
        layout.addWidget(axis_group)
        
        # Sensitivity Group
        sensitivity_group = QGroupBox("Sensitivity")
        sensitivity_layout = QVBoxLayout()
        
        # Pan sensitivity
        pan_layout = QHBoxLayout()
        pan_layout.addWidget(QLabel("Pan Sensitivity:"))
        self.pan_sensitivity_spin = QDoubleSpinBox()
        self.pan_sensitivity_spin.setRange(0.001, 0.1)
        self.pan_sensitivity_spin.setSingleStep(0.001)
        self.pan_sensitivity_spin.setDecimals(3)
        self.pan_sensitivity_spin.setValue(0.005)
        pan_layout.addWidget(self.pan_sensitivity_spin)
        sensitivity_layout.addLayout(pan_layout)
        
        # Zoom sensitivity
        zoom_layout = QHBoxLayout()
        zoom_layout.addWidget(QLabel("Zoom Sensitivity:"))
        self.zoom_sensitivity_spin = QDoubleSpinBox()
        self.zoom_sensitivity_spin.setRange(0.001, 0.1)
        self.zoom_sensitivity_spin.setSingleStep(0.001)
        self.zoom_sensitivity_spin.setDecimals(3)
        self.zoom_sensitivity_spin.setValue(0.01)
        zoom_layout.addWidget(self.zoom_sensitivity_spin)
        sensitivity_layout.addLayout(zoom_layout)
        
        # Deadzone
        deadzone_layout = QHBoxLayout()
        deadzone_layout.addWidget(QLabel("Deadzone:"))
        self.deadzone_spin = QDoubleSpinBox()
        self.deadzone_spin.setRange(0.0, 0.2)
        self.deadzone_spin.setSingleStep(0.01)
        self.deadzone_spin.setDecimals(2)
        self.deadzone_spin.setValue(0.05)
        deadzone_layout.addWidget(self.deadzone_spin)
        sensitivity_layout.addLayout(deadzone_layout)
        
        sensitivity_group.setLayout(sensitivity_layout)
        layout.addWidget(sensitivity_group)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        # Add Reset to Defaults button
        reset_button = QPushButton("Reset to Defaults")
        reset_button.clicked.connect(self.reset_to_defaults)
        button_box.addButton(reset_button, QDialogButtonBox.ResetRole)
        
        layout.addWidget(button_box)
        
        self.setLayout(layout)
    
    def update_axis_explanation(self):
        """Update the explanation text based on swap setting"""
        if self.swap_yz_cb.isChecked():
            text = "• Forward/Back → Pan map up/down\n• Up/Down → Zoom in/out"
        else:
            text = "• Forward/Back → Zoom in/out\n• Up/Down → Pan map up/down"
        self.axis_explanation.setText(text)
    
    def get_settings(self):
        """Get current settings from the dialog"""
        self.settings['invert_x'] = self.invert_x_cb.isChecked()
        self.settings['invert_y'] = self.invert_y_cb.isChecked()
        self.settings['invert_z'] = self.invert_z_cb.isChecked()
        self.settings['swap_yz'] = self.swap_yz_cb.isChecked()
        self.settings['pan_sensitivity'] = self.pan_sensitivity_spin.value()
        self.settings['zoom_sensitivity'] = self.zoom_sensitivity_spin.value()
        self.settings['deadzone'] = self.deadzone_spin.value()
        return self.settings
    
    def set_settings(self, settings):
        """Load settings into the dialog"""
        self.settings = settings
        self.invert_x_cb.setChecked(settings.get('invert_x', False))
        self.invert_y_cb.setChecked(settings.get('invert_y', False))
        self.invert_z_cb.setChecked(settings.get('invert_z', False))
        self.swap_yz_cb.setChecked(settings.get('swap_yz', True))
        self.pan_sensitivity_spin.setValue(settings.get('pan_sensitivity', 0.005))
        self.zoom_sensitivity_spin.setValue(settings.get('zoom_sensitivity', 0.01))
        self.deadzone_spin.setValue(settings.get('deadzone', 0.05))
    
    def reset_to_defaults(self):
        """Reset all settings to default values"""
        self.invert_x_cb.setChecked(False)
        self.invert_y_cb.setChecked(False)
        self.invert_z_cb.setChecked(False)
        self.swap_yz_cb.setChecked(True)
        self.pan_sensitivity_spin.setValue(0.005)
        self.zoom_sensitivity_spin.setValue(0.01)
        self.deadzone_spin.setValue(0.05)
