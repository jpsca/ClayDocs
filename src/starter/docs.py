import jinjax_ui
from claydocs import Docs


pages = [
    "index.md",
]

docs = Docs(pages, add_ons=[jinjax_ui])
docs.add_folder("components")
docs.add_folder("theme")

if __name__ == "__main__":
    docs.run()
