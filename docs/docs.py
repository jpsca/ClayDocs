from claydocs import Docs, theme_path


pages = [
    "index.md",
    "internal.md",
]

docs = Docs(
    pages,
    search=False,
    theme=theme_path,
)

if __name__ == "__main__":
    docs.run()
