import shutil
import sys
from pathlib import Path


DEFAULT_PATH = "./docs"
STARTER = Path(__file__).parent.parent / "starter"


def run():
    _, *sysargs = sys.argv
    dst = Path(sysargs[0] if sysargs else DEFAULT_PATH)
    if dst.exists():
        print(f"Path {dst} already exists")
        return

    print(f"Creating the starter project at `{dst}`...")
    shutil.copytree(STARTER, dst)
    print("✨ Done! ✨")
