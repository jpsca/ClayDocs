import jinjax_ui
from claydocs import Docs, theme


pages = [
    "index.mdx",
]

docs = Docs(
    pages,
    add_ons=[theme, jinjax_ui]
)


if __name__ == "__main__":
    docs.run()
