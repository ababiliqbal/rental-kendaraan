from django import template

register = template.Library()

@register.filter(name='eq')
def eq(value, arg):
    """
    Membandingkan apakah value == arg.
    Cara pakai di template: 
    {% if variable|eq:"string" %}
    """
    return value == arg