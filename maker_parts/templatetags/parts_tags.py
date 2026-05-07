from django import template
from maker_parts.models import ProjectPart

register = template.Library()


# BOM Bill of Materials, AKA Parts list, used to calc total cost
@register.simple_tag
def bom_total(project):
    """
    Usage in template:
        {% load parts_tags %}
        {% bom_total project as total %}
        {% if total %}${{ total }}{% endif %}
    """
    return ProjectPart.bom_total(project)
