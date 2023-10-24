from django.apps import AppConfig
from django.db.models.signals import post_migrate


default_calconc_users = ['Administrador', 'Consultor', 'Editor']


class UsuariosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'usuarios'

    def ready(self):
        from .signals import populate_models
        post_migrate.connect(populate_models, sender=self)

        # from django.contrib.auth.models import Group
        #
        # for group in default_calconc_users:
        #     Group.objects.get_or_create(name=group)
