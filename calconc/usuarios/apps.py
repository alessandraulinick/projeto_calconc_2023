from django.apps import AppConfig


class UsuariosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'usuarios'

    def ready(self):
        from django.contrib.auth.models import Group

        Group.objects.get_or_create(name='Administrador')
        Group.objects.get_or_create(name='Consultor')
        Group.objects.get_or_create(name='Editor')
