from django import  template
from ..models import *
register = template.Library()

@register.filter(name='split')
def split(value,arg):
    "function:same with split"
    val = value.split(arg,-1)
    return val[-1]

@register.filter(name='transform')
def transform(value):
    "function:same with split"
    val = value.strip('_ext')
    val = SubjectTheme.objects.get(id=int(val))
    return val