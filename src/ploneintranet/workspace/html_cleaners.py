# -*- coding: utf-8 -*-

from lxml import etree
from lxml import html
from htmllaundry import utils
from htmllaundry.cleaners import LaundryCleaner
from htmllaundry.utils import MARKER
from htmllaundry.utils import INLINE_TAGS

# Define our own DocumentCleaner, in order to fine-tune which tags are allowed
DocumentCleaner = LaundryCleaner(
    page_structure=False,
    remove_unknown_tags=False,
    allow_tags=[
        'a', 'img', 'em', 'p', 'strong',
        'h1', 'h2', 'h3', 'h4', 'h5', 'ul', 'ol', 'li', 'sub', 'sup',
        'abbr', 'acronym', 'dl', 'dt', 'dd', 'cite',
        'dft', 'br', 'table', 'tr', 'td', 'th', 'thead',
        'tbody', 'tfoot'],
    safe_attrs_only=True,
    add_nofollow=True,
    scripts=True,
    javascript=True,
    comments=False,
    style=True,
    links=False,
    meta=False,
    processing_instructions=False,
    frames=True,
    annoying_tags=False
)


def _wrap_text(doc, element='p'):
    """
        Make sure there is no unwrapped text at the top level. Any bare text
        found is wrapped in a `<p>` element (or alternative element that gets
        passed in to this method).
        In addition to what htmllaundry does, also any bare inline tags get
        wrapped, so that no `<em>`, `<strong>`, etc. tags will float around
        outside of a paragraph.
    """
    def par(text):
        el = etree.Element(element, {MARKER: ''})
        el.text = text
        return el

    def wrapper_par(el):
        wrapper = etree.Element(element, {MARKER: ''})
        wrapper.insert(0, el)
        return wrapper

    if doc.text:
        doc.insert(0, par(doc.text))
        doc.text = None

    while True:
        for (i, el) in enumerate(doc):
            if html._nons(el.tag) in INLINE_TAGS:
                if i and MARKER in doc[i - 1].attrib:
                    doc[i - 1].append(el)
                    break
                else:
                    doc.insert(i, wrapper_par(el))
                    break
            if not utils.is_whitespace(el.tail):
                doc.insert(i + 1, par(el.tail))
                el.tail = None
                break
        else:
            break

    for el in doc:
        if MARKER in el.attrib:
            del el.attrib[MARKER]


def sanitize_html(input, cleaner=DocumentCleaner, wrap='p'):
    """Clean up markup using a given cleanup configuration.
       Unwrapped text will be wrapped with wrap parameter.
    """
    if 'body' not in cleaner.allow_tags:
        cleaner.allow_tags.append('body')

    input = u"<html><body>%s</body></html>" % input
    document = html.document_fromstring(input)
    bodies = [e for e in document if html._nons(e.tag) == 'body']
    body = bodies[0]

    cleaned = cleaner.clean_html(body)
    utils.remove_empty_tags(cleaned)
    utils.strip_outer_breaks(cleaned)

    if wrap is not None:
        if wrap in html.defs.tags:
            _wrap_text(cleaned, wrap)
        else:
            raise ValueError(
                'Invalid html tag provided for wrapping the sanitized text')

    output = u''.join([
        etree.tostring(fragment, encoding='unicode')
        for fragment in cleaned.iterchildren()])
    if wrap is None and cleaned.text:
        output = cleaned.text + output

    return output
