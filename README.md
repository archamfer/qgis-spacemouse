# SpaceMouse Navigation for QGIS

Navigate QGIS 2D maps naturally using your 3Dconnexion SpaceMouse device.

![Plugin Demo](screenshot.png)

## Features

- 🖱️ **Smooth 2D Navigation**: Pan and zoom your QGIS maps using your SpaceMouse
- ⚙️ **Customizable Controls**: Invert any axis or swap Y/Z axes to match your preference
- 🎚️ **Adjustable Sensitivity**: Fine-tune pan and zoom speeds to your liking
- 💾 **Persistent Settings**: Your configuration is saved between sessions
- 🔌 **Plug and Play**: Automatically detects connected 3Dconnexion devices

## Supported Devices

This plugin supports most 3Dconnexion SpaceMouse devices, including:
- SpaceMouse Compact
- SpaceMouse Wireless
- SpaceMouse Pro
- SpaceMouse Enterprise
- And other 3Dconnexion devices

## Installation

### Prerequisites

1. **3Dconnexion Driver**: Install the official 3Dconnexion driver from [3dconnexion.com](https://3dconnexion.com/us/drivers/)
2. **Python HID Library**: Install in QGIS Python environment

#### Installing HID Library

Open the **OSGeo4W Shell** (comes with QGIS) and run:

```bash
pip install hid
```

Or from the QGIS Python Console:

```python
import subprocess
import sys
subprocess.check_call([sys.executable, "-m", "pip", "install", "hid"])
```

### Plugin Installation

#### Method 1: From QGIS Plugin Repository (when published)

1. Open QGIS
2. Go to `Plugins` → `Manage and Install Plugins`
3. Search for "SpaceMouse Navigation"
4. Click `Install Plugin`

#### Method 2: Manual Installation

1. Download the latest release
2. Extract to your QGIS plugins folder:
   - **Windows**: `C:\Users\YourUsername\AppData\Roaming\QGIS\QGIS3\profiles\default\python\plugins\`
   - **Mac**: `~/Library/Application Support/QGIS/QGIS3/profiles/default/python/plugins/`
   - **Linux**: `~/.local/share/QGIS/QGIS3/profiles/default/python/plugins/`
3. Restart QGIS
4. Enable the plugin in `Plugins` → `Manage and Install Plugins` → `Installed`

## Usage

1. **Enable the Plugin**: Click the SpaceMouse toolbar button or go to `Plugins` → `SpaceMouse Navigation` → `Enable SpaceMouse`
2. **Configure Settings**: Go to `Plugins` → `SpaceMouse Navigation` → `SpaceMouse Settings` to customize:
   - Axis inversions (flip left/right, forward/back, up/down)
   - Axis swapping (swap which axis controls panning vs zooming)
   - Pan and zoom sensitivity
   - Deadzone (ignore small movements)
3. **Navigate**: Move your SpaceMouse to pan and zoom the map!

### Default Controls

- **Left/Right**: Pan map left/right
- **Forward/Back**: Pan map up/down
- **Up/Down**: Zoom in/out

All controls can be customized in the settings dialog.

## Troubleshooting

### Plugin doesn't load
- Make sure the `hid` library is installed (see Installation section)
- Check the QGIS Python Console for error messages

### No device detected
- Ensure your SpaceMouse is plugged in
- Try closing the 3Dconnexion settings application
- On Windows, you may need to temporarily disable the 3Dconnexion service if it's capturing all device input

### Movement is too sensitive/not sensitive enough
- Open the settings dialog and adjust the sensitivity values
- Start with small adjustments (0.001 increments)

### Wrong direction mappings
- Use the settings dialog to invert individual axes
- Use "Swap Y/Z axes" to change which axis controls panning vs zooming

## Development

### Project Structure

```
spacemouse_navigation/
├── __init__.py              # Plugin entry point
├── spacemouse_plugin.py     # Main plugin logic
├── settings_dialog.py       # Settings UI
├── metadata.txt             # Plugin metadata
├── icon.png                 # Plugin icon
└── README.md               # This file
```

### Building from Source

```bash
git clone https://github.com/archamfer/qgis-spacemouse.git
cd qgis-spacemouse
# Copy to QGIS plugins folder
```

### Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This plugin is released under the GNU General Public License v2 or later.

## Credits

Created by Jacob Strange + Claude

## Support

- Report issues: [GitHub Issues](https://github.com/archamfer/qgis-spacemouse/issues)
- Questions: [GitHub Discussions](https://github.com/archamfer/qgis-spacemouse/discussions)

## Changelog

### Version 1.0.0 (2025-10-23)
- Initial release
- Support for 3Dconnexion SpaceMouse devices
- Customizable axis inversion and swapping
- Adjustable sensitivity settings
- Persistent configuration
