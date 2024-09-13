from django.contrib import admin
from django.apps import apps
from .models import *

# Get all models from the current app
models = apps.get_models()

# Loop through all models and register them to the admin site
for model in models:
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass  # If the model is already registered, skip it
