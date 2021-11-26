import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myswitch.settings")

# your imports, e.g. Django models
from myswitch.models import Machine

# From now onwards start your script..
m = Machine()
m.name = 'Test'
m.save()
