'''
# HTML Outliner

Wraps the document logical sections (as implied by h1-h6 headings)
and returns the modified html plus the page table of contents in the
format of the markdown's `toc` extension.

Usage
-----

    >>> html = """
    ... <h1>1</h1>
    ... <p>Section 1</p>
    ... <h2>1<b>.</b>1</h2>
    ... <p>Subsection 1.1</p>
    ... <h2>1.2</h2>
    ... <p>Subsection 1.2</p>
    ... <h3>1.2.1</h3>
    ... <p>Hey 1.2.1 Special section</p>
    ... <h3>1.2.2</h3>
    ... <h4>1.2.2.1</h4>
    ... <h1>2</h1>
    ... <p>Section 2</p>
    ... """.strip()
    >>> html, page_toc = outline(html)

    >>> print(html)
    <section class="section1" id="s-1"><h1>1</h1>
    <p>Section 1</p>
    <section class="section2" id="s-11"><h2>1<b>.</b>1</h2>
    <p>Subsection 1.1</p>
    </section><section class="section2" id="s-12"><h2>1.2</h2>
    <p>Subsection 1.2</p>
    <section class="section3" id="s-121"><h3>1.2.1</h3>
    <p>Hey 1.2.1 Special section</p>
    </section><section class="section3" id="s-122"><h3>1.2.2</h3>
    <section class="section4" id="s-1221"><h4>1.2.2.1</h4>
    </section></section></section></section><section class="section1" id="s-2"><h1>2</h1>
    <p>Section 2</p></section>

    >>> print(page_toc)
    [{'level': 1, 'id': 's-1', 'name': '1', 'children': [{'level': 2, 'id': 's-11', 'name': '1.1', 'children': []}, {'level': 2, 'id': 's-12', 'name': '1.2', 'children': [{'level': 3, 'id': 's-121', 'name': '1.2.1', 'children': []}, {'level': 3, 'id': 's-122', 'name': '1.2.2', 'children': [{'level': 4, 'id': 's-1221', 'name': '1.2.2.1', 'children': []}]}]}]}, {'level': 1, 'id': 's-2', 'name': '2', 'children': []}]

Consecutive headers aren't a problem:

    >>> html="""
    ... <h1>ONE</h1>
    ... <h3>TOO Deep</h3>
    ... <h2>Level 2</h2>
    ... <h1>TWO</h1>
    ... """.strip()
    >>> html, page_toc = outline(html)

    >>> print(html)
    <section class="section1" id="s-one"><h1>ONE</h1>
    <section class="section3" id="s-too-deep"><h3>TOO Deep</h3>
    </section><section class="section2" id="s-level-2"><h2>Level 2</h2>
    </section></section><section class="section1" id="s-two"><h1>TWO</h1></section>

    >>> print(page_toc)
    [{'level': 1, 'id': 's-one', 'name': 'ONE', 'children': [{'level': 3, 'id': 's-too-deep', 'name': 'TOO Deep', 'children': []}, {'level': 2, 'id': 's-level-2', 'name': 'Level 2', 'children': []}]}, {'level': 1, 'id': 's-two', 'name': 'TWO', 'children': []}]

'''
from bs4 import BeautifulSoup, NavigableString

from markdown.extensions.toc import nest_toc_tokens, slugify_unicode


HEADERS = ["h1", "h2", "h3", "h4", "h5", "h6"]


def outline(html, id_prefix="s", wrapper_cls="section%(LEVEL)d"):
    soup = BeautifulSoup(html, 'html.parser')

    toc_tokens = []
    for child in soup.find_all(HEADERS):
        depth = int(child.name[1])  # type: ignore
        header_text = ''.join(child.text).strip()
        header_id = f"{id_prefix}-{slugify_unicode(header_text, separator='-')}"
        toc_tokens.append({"level": depth, "id": header_id, "name": header_text})
    page_toc = nest_toc_tokens(toc_tokens)

    stack = []
    root = soup.new_tag("div")  # Create a root element to hold everything

    for child in list(soup.children):
        if isinstance(child, NavigableString):
            if stack:
                stack[-1][0].append(child.extract())
            else:
                root.append(child.extract())
            continue

        name = child.name  # type: ignore

        if name and name.lower() in HEADERS:
            depth = int(name[1])  # type: ignore
            header_text = ''.join(child.text).strip()
            header_id = f"{id_prefix}-{slugify_unicode(header_text, separator='-')}"

            section = soup.new_tag("section")
            section['id'] = header_id
            section['class'] = wrapper_cls % {"LEVEL": depth}

            while stack and stack[-1][1] >= depth:
                stack.pop()

            if stack:
                stack[-1][0].append(section)
            else:
                root.append(section)

            section.append(child.extract())
            stack.append((section, depth))
        elif stack:
            stack[-1][0].append(child.extract())
        else:
            root.append(child.extract())

    html = "".join(str(child) for child in root.children).strip()

    return html, page_toc
