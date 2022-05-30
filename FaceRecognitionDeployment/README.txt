#RUN ALL THE COMMANDS IN A POWERSHELL

---------- DEPLOYMENT ---------------------------------------

 Run the deployment:

$ cd FaceRecognitionDeployment
$ docker-compose up             # if this fails, retry the command since the database might not have initialized on time

 Connect to the Web docker container and run:

$ cd /code
$ python3 manage.py migrate


---------- COMMANDS OF INTEREST ---------------------------------------

 In case of modifying the models, changes on the database can be applied by running:

$ python3 manage.py check <django_app>
$ python3 manage.py makemigrations
$ python3 manage.py migrate
$ python3 manage.py sqlmigrate authentication 0001


 To create a superuser:

$ python3 manage.py createsuperuser


 Start the deployment:

$ docker-compose run web django-admin startproject <django-project> .