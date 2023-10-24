def populate_models(sender, **kwargs):
    from django.contrib.auth.models import User
    from django.contrib.auth.models import Group
    from .apps import default_calconc_users

    for group in default_calconc_users:
        Group.objects.get_or_create(name=group)
