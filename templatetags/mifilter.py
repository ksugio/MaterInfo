from django import template
from django.template.defaultfilters import stringfilter
import markdown

register = template.Library()

@register.filter
@stringfilter
def markdown2html(value):
    extensions = ['markdown.extensions.extra', 'toc', 'fenced_code']
    return markdown.markdown(value, extensions=extensions)
