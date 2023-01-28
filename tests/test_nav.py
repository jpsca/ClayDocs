from claydocs.nav import Nav


def test_toc():
    nav = Nav("", [
        ["1.mdx", "One"],
        ["a", [
            ["2.mdx", "Two"],
            ["3.mdx", "Three"],
            ["b", [
                ["4.mdx", "Four"],
                ["c", [
                    ["5.mdx", "Five"],
                ]],
            ]],
        ]],
        ["6.mdx", "Six"],
    ])

    assert nav.titles == {
        "/1": {"url": "/1", "title": "One", "index": 0, "section": ""},
        "/2": {"url": "/2", "title": "Two", "index": 1, "section": "a"},
        "/3": {"url": "/3", "title": "Three", "index": 2, "section": "a"},
        "/4": {"url": "/4", "title": "Four", "index": 3, "section": "b"},
        "/5": {"url": "/5", "title": "Five", "index": 4, "section": "c"},
        "/6": {"url": "/6", "title": "Six", "index": 5, "section": ""},
    }

    assert nav.toc == [
        ["/1", "One"],
        ["a", [
            ["/2", "Two"],
            ["/3", "Three"],
            ["b", [
                ["/4", "Four"],
                ["c", [
                    ["/5", "Five"],
                ]],
            ]],
        ]],
        ["/6", "Six"],
    ]


def test_next():
    nav = Nav("", [
        ["1.mdx", "One"],
        ["a", [
            ["2.mdx", "Two"],
            ["3.mdx", "Three"],
            ["b", [
                ["4.mdx", "Four"],
                ["c", [
                    ["5.mdx", "Five"],
                ]],
            ]],
        ]],
        ["6.mdx", "Six"],
    ])

    assert nav._get_next("1") == ("a", "/2", "Two")
    assert nav._get_next("2") == ("a", "/3", "Three")
    assert nav._get_next("3") == ("b", "/4", "Four")
    assert nav._get_next("4") == ("c", "/5", "Five")
    assert nav._get_next("5") == ("", "/6", "Six")
    assert nav._get_next("6") == ("", "", "")


def test_prev():
    nav = Nav("", [
        ["1.mdx", "One"],
        ["a", [
            ["2.mdx", "Two"],
            ["3.mdx", "Three"],
            ["b", [
                ["4.mdx", "Four"],
                ["c", [
                    ["5.mdx", "Five"],
                ]],
            ]],
        ]],
        ["6.mdx", "Six"],
    ])

    assert nav._get_prev("6") == ("c", "/5", "Five")
    assert nav._get_prev("5") == ("b", "/4", "Four")
    assert nav._get_prev("4") == ("a", "/3", "Three")
    assert nav._get_prev("3") == ("a", "/2", "Two")
    assert nav._get_prev("2") == ("", "/1", "One")
    assert nav._get_prev("1") == ("", "", "")
