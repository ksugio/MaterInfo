# About MaterInfo
MaterInfo is a web application for materials informatics.
This application can be used to collect data, extract features, collect features,
select features, machine learning, and perform inverse analysis.
It also has extensive research support functions such as diagram creation,
reference management, document version control, schedule management,
questionnaire functions, and bulletin boards.

[Japanese version README](README-ja.md)

# Run on Windows

Download and install Docker Desktop for Windows from [site](https://www.docker.com/products/docker-desktop/).

Download [compose.yaml](https://github.com/ksugio/MaterInfo/blob/main/compose.yaml)
and place it in an appropriate location.
Launch a command prompt, move to the folder where compose.yaml is located,
Create and start a Docker container with the following command.
```
docker compose up -d
```
Once the container has been successfully created and started, launch the materinfo shell.
````
docker compose exec materinfo /bin/bash
````
Perform migration, create administrative users, and collect static files.
````
(materinfo) python manage.py migrate
(materinfo) python manage.py createsuperuser
(materinfo) python manage.py collectstatic
````
Restart the Docker container.
When you access [http://localhost:8080/](http://localhost:8080/),
a login screen will appear, so log in with the administrator user you created.
