# myapp/resources.py

from import_export import resources
from .models import MyModel

class MyModelResource(resources.ModelResource):
    class Meta:
        model = MyModel
