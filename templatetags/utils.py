from django import template

register = template.Library()

@register.filter
def get_class(value):
    return value.__class__.__name__

@register.filter
def get_path(value):
    titles = []
    while True:
        if hasattr(value, 'title'):
            titles.append(value.title)
        elif hasattr(value, 'prefix'):
            titles.append(value.prefix)
        if value.upper:
            value = value.upper
        else:
            break
    titles = titles[::-1]
    path = titles[0]
    for title in titles[1::]:
        if isinstance(title, str):
            path += ' / ' + title
        elif callable(title):
            path += ' / ' + title()
    return path

@register.filter
def get_dict_value(d, k):
    if (k in d.keys()):
        return d[k]
    else:
        return None
