from django.http import HttpResponse
from django.shortcuts import redirect

# TODO - adicionar isso, não permite usuário ir para a tela de login se já estiver logado
# https://www.youtube.com/watch?v=eBsc65jTKvw
# def unauthenticated_user(view_func):
#     def wrapper_func(request, *args, **kwargs):
#
#         return view_func(request, *args, **kwargs)
#
#     return wrapper_func()


def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            group = None
            if request.user.groups.exists():
                group = request.user.groups.all()[0].name.lower()

            if group in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                # todo redirecionar para uma tela bonitinha
                return HttpResponse('não autorizado')
        return wrapper_func
    return decorator
