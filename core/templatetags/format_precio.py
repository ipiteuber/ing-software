from django import template

register = template.Library()

@register.filter
def formato_clp(value):
    try:
        value = int(value)
        formatted = f"{value:,}".replace(",", ".")
        return f"${formatted}"
    except (ValueError, TypeError):
        return value
