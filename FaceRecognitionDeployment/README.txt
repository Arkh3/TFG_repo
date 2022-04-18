#RUN ALL THE COMMANDS IN A POWERSHELL

Start the deployment:
docker-compose run web django-admin startproject <django-project> .

Run the deployment:
docker-compose up

Connect to the docker:/code and run
python3 manage.py migrate



-------------------------------------------------

python3 manage.py check authentication
python3 manage.py makemigrations
python3 manage.py sqlmigrate authentication 0001