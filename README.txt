- A los campos de las formularios añadirles los len(), required, show_hidden....
- Hacer que se pasen los datos de un formulario a otro: 
    op1) se apssan los datos de un orm al otro por la url o por dnd sea
    op2) hacemos 2 consulatas a la bbdd, dejando algun campo null en la primera, que llenameros en la seg
    op3) ??
- 'Es muy importante dar un nombre a las rutas por si lasnecesitamos dentro del programa. Nunca debemos escribir las URL a
    mano dentro de nuestro programa' APUNTES DE GIW
- usar {% if request.user.username %}{% else %}{% endif %} en logged user 
- AHORA MISMO ESTA UN POCO GUARRO, PUES SE LO PASO COMO ARG DE UNA CLASE A OTRA Y LOS TENGO OCULTOS EN EL FORM
- SE QUE LAS PASSWORD DEBERIAN ESTAR EN EL PRIMER REGSITRO, ERA PARA PROBAR SOLO EL PASO DE DATOS
- eL REGISTRO 3E ES PARA VER COMO QUEDARIA SI LO HACEMOS TODO DIRECTAMENTE EN UNA VISTA
----------------------------
----------------------------
En registro uno cambiar el <a href="{% url 'login' %}" class="justify-content-center">
y al ser login creo que sería post