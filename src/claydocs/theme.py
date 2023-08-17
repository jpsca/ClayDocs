from pathlib import Path

from jinjax_ui import components_path as ui_components


root = Path(__file__).parent.parent
components = {
    "T": root / "theme",
    "": root / "components",
    "UI": ui_components,
}
