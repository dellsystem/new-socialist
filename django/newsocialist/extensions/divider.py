import re

import markdown


DIVIDER_RE = r'^\[divider\]'
class DividerPattern(markdown.inlinepatterns.Pattern):
    def handleMatch(self, m):
        """
        When a line starts with
        [divider]
        it's replaced by a nested div pattern.
        """
        divider_el = markdown.util.etree.Element('div')
        divider_el.set('class', 'divider')
        mask_el = markdown.util.etree.SubElement(divider_el, 'div')
        mask_el.set('class', 'dividermask')
        span_el = markdown.util.etree.SubElement(divider_el, 'span')
        i_el = markdown.util.etree.SubElement(span_el, 'i')
        return divider_el


class DividerExtension(markdown.Extension):
    def extendMarkdown(self, md, md_globals):
        md.inlinePatterns['divider'] = DividerPattern(DIVIDER_RE, md)


def makeExtension(*args, **kwargs):
    return DividerExtension(*args, **kwargs)
