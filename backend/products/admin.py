from django.contrib import admin

# Register your models here.
def register_models(models):
    for model in models:
        admin.site.register(model)