from drf_yasg import openapi

tags_auth = ['Auth']
tags_students = ['Students']
tags_excel = ['Excel']

login = {
    'operation_description': '## Авторизация пользователя',
    'operation_summary': 'Авторизация пользователя',
    'tags': tags_auth,
}