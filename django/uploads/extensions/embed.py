import markdown

from uploads.models import PdfUpload, ImageUpload


EMBED_RE = r'\[(pdf|img):([a-z0-9-]+) ?([^\]]*)\]'
class EmbedPattern(markdown.inlinepatterns.Pattern):
    def handleMatch(self, m):
        embed_type = m.group(2)
        slug = self.unescape(m.group(3))
        caption = self.unescape(m.group(4))
        if embed_type == 'pdf':
            pdf_upload = PdfUpload.objects.filter(slug=slug).first()
            if pdf_upload:
                object_el = markdown.util.etree.Element('object')
                path = pdf_upload.file.url
                object_el.set('data', path)
                object_el.set('type', 'application/pdf')
                object_el.set('width', '100%')
                object_el.set('height', '800px')
                iframe_el = markdown.util.etree.SubElement(object_el, "iframe")
                iframe_el.set('src', path)
                iframe_el.set('width', '100%')
                iframe_el.set('height', '800px')
                iframe_el.text = 'Please download the PDF'
                return object_el
            else:
                return 'INVALID FILE: ' + slug
        elif embed_type == 'img':
            image_upload = ImageUpload.objects.filter(slug=slug).first()
            if image_upload:
                div_el = markdown.util.etree.Element('div')
                div_el.set('class' , 'uploaded-image')
                image_el = markdown.util.etree.SubElement(div_el, 'img')
                image_el.set('src', image_upload.file.url)
                span_el = markdown.util.etree.SubElement(div_el, 'span')
                span_el.text = caption
                return div_el
            else:
                return 'INVALID FILE: ' + slug


class EmbedExtension(markdown.Extension):
    def extendMarkdown(self, md, md_globals):
        md.inlinePatterns['embed'] = EmbedPattern(EMBED_RE, md)


def makeExtension(*args, **kwargs):
    return EmbedExtension(*args, **kwargs)
