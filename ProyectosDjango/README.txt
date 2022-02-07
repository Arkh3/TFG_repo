1# Crear bbdd (YA NO HACE FALTA HACER ESTO, SOLO LA 1ª VEZ)
python manage.py migrate

2# Arrancar el proyecto, el servidor
python manage.py runserver

3# Para verlo en el navegador la ruta actual es
http://127.0.0.1:8000/saludo/
http://127.0.0.1:8000/login/

4# Otros
Dentro de un proyecto Django se pueden crear como varias apps, no se si estará bien las rutas de este proyecto o prefieres meter algo dentro de otra carpeta. Por ejemplo, la carpeta de plantillas la habia metido dentro de la segunda carpeta de TFGweb pero al final la saque una para atras para que fuera bien una cosilla xd

4# Crear superusuario desde consola para poder usar admin (PARA MÁS ADELANTE)
python manage.py createsuperuser
http://localhost:8000/admin