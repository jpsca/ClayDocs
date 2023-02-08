from pathlib import Path

from jinjax_ui import components_path as ui_components


root = Path(__file__).parent.parent
components = {
    "t": root / "theme",
    "": root / "components",
    "ui": ui_components,
}
