import jinjax_ui
from claydocs import Docs


pages = [
    "index.md",
]

docs = Docs(pages, add_ons=[jinjax_ui])


if __name__ == "__main__":
    docs.run()
