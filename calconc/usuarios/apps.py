from django.apps import AppConfig


default_calconc_users = ['Administrador', 'Consultor', 'Editor']


class UsuariosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'usuarios'

    def ready(self):
        from django.contrib.auth.models import Group

        for group in default_calconc_users:
            Group.objects.get_or_create(name=group)
