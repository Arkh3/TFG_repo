#RUN ALL THE COMMANDS IN A POWERSHELL

Start the deployment:
docker-compose run web django-admin startproject <django-project> .

Run the deployment:
docker-compose up (if this fails retry since the database might not have initialized on time)

Connect to the docker:/code and run
python3 manage.py migrate



-------------------------------------------------

python3 manage.py check authentication
python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py sqlmigrate authentication 0001
python3 manage.py createsuperuser