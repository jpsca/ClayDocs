from claydocs import Docs

nav = [
    "index.md",
    (
        "Guide",
        (
            "guide/index.md",
            "guide/attributes.md",
            "guide/extra.md",
            "guide/css_and_js.md",
        ),
    ),
]

docs = Docs(nav)


if __name__ == "__main__":
    docs.serve()
