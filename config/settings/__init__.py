import os

env = os.environ.get("DJANGO_SETTINGS_MODULE", "")

if env.endswith("production"):
    from .production import *
else:
    from .local import *