# Dockerized Web Scrapper with (Beautiful Soup + Django + Mongo)

### Project Preparation
---

***N.B:*** It is assumed that Docker and docker-compose is already installed into the user's system.

---

- Download the application from github
- Extract the project.
- Copy ``.env.example`` or Rename it to ``.env``. (This contains the projectwise environment keys)
- Now open terminal and hit the command:

```bash
docker-compose build
```

### Create Superuser
---
The docker-container for Django and MongoDB is now build but not running yet. However, we need a superuser to login into the admin panel once it is up and running. Therefore, before running the application project a superuser needs to be created with the command:

```bash
docker-compose run django python manage.py createsuperuser
```

### Run Test
---
In order to Run the test run the command:
```bash
docker-compose run django python manage.py test
```

### Run The Application
---

In order to run the application hit the following command.

```bash
docker-compose up -d
```

Alternatively, the project could be build and run in one go with the command:

```bash
docker-compose up --build -d
```

This will make the container to run in the background.

***Now visit csee the scrapped data lists.***

***In order to see the admin panel visit http://localhost:8000/admin/***