*****************versiones*******************
python 3.9.7 (instalacion de libreria psycopg2)
django 4.1.5
postgres 6.18-6.21

********instalacion de psycopg2***************
~:pip install psycopg2

*********credenciales sistema de inventario*******************

Usuario administrador: jjiatz
Contraseña: Dj@ngo20.23


********GIT*************
user.name "jjiatz"
user.email "jjiatzg@miumg.edu.gt"

*********GITHUB***********
repository name: project-inv
Description: proyectopg


$git add .	-(agregar todos los archivos)
$git commit -m "comentario"	-(commit con comentario)
$git push -u origin master	-(subir github)

$git status	-(observar los cambios modificados o afectados sin add y commit)
$git log	-(observar los commit relizados y comentario de cada uno de ellos)


************ instalacion para reportes*****************************

~:pip install xhtml2pdf

************ instalacion modelo usuarios ******************

~:pip install django-userforeignkey

luego agregar al settings.py

INSTALLED_APPS = [
    'django-userforeignkey'
]

MIDDLEWARE = [
    'django_userforeignkey.middleware.UserForeignKeyMiddleware',
]

************ instalacion django rest framework ******************
~:pip install djangorestframework

luego agregar al settings.py

INSTALLED_APPS = [
    'rest_framework'
]