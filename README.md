ṭ
DiscoG is an E-Learning platform, developed under the vision of Gerard Papet. This document aims to explain the working of the entire application, from both the technical and the functional perspective.

## Technologies Used
The application is divided into 2 parts as all applications are. One is the backend which is written in [Python] programming language, with the help of [Django] framework. The frontend is written in using HTML, CSS, and Javascript with the help of [Jquery] to perform actions [asynchronously].

For the database side, we use [Postgresql] for its ability to implement native signals, performance, and extensibility.

For storing and serving the static files, we use [AWS's S3 Bucket]. The reason behind this is explained down below.

## Initial setup
Initializing and running the application is quite simple. There are two ways you can run the application, you can either chose to build a [Docker image] using Docker. Or you can manually install the dependencies.

### Docker Method
You'll need to install docker first, you can do this by using `sudo apt install docker.io` if you're running on an Ubuntu-based machine. If not, simply follow the instructions on [Docker.com].

Once installed, clone the repository to your environment and `cd` into it. Once inside the directory simply use

`docker-compose up -d --build`

You'll need to be in `docker` group to run this command, if you're not in that group, simply add yourself in it using `sudo usermod -aG docker $USER`. If you don't want to do that, append `sudo` at the beginning of every docker command.

*NOTE - You'll need to install `docker-compose` as well if you want to use this method. Follow this [link to install] `docker-compose`.*

Once you run the aforementioned command, you'll see docker going through all the steps to set up the environment.

If you want to verify if the build was successful you can simply use `docker ps -a`. It should list all the docker processes running. To visit the project you can navigate to, `http://<host>/`

### Manually Initialization
The second method is straight forward, even though it's manual. You'll need to first create a database on Postgresql DB instance.

The first thing to do here is to login to a Postgresql shell.

`psql -U postgres`

If you get an error that pretty much says "You don't have the permission to access it or the password doesn't match." You'll need to log in using the `sudo` prefix.

`sudo psql -U postgres`

This should give you a postgresql DB shell. Time to create your database.

`postgres=# create database <database_name>`

You can verify that the database has been created by using `\l` in your DB shell. It will list all the databases in that instance.

Now to set up some environment variables now. Open `entrypoint.sh`, you'll see some `export` variables, you'll need to add values to all of them.

```
export DISCOG_DEV_DB=<database-name>
export POSTGRES_USER=<postgresql-username>
export POSTGRES_USER_PASSWORD=<postgresql-password>
export SENTRY_DNS=<sentry-DNS>
```

More explanation on what is sentry and how to configure it is provided down below, in the maintenance and logging section.


Once you're done with all of that, it's time to create a virtual environment for your project.

*Note - Virtual environment is used by Python to separate the dependencies for each and every Python project*

To create the virtual environment, simply use the following commands.

```bash
python3.8 -m pip install virtualenv
python3.8 -m virtualenv <name_of_the_virtualenv>
```

Once the creation of the virtualenvironment is done, you'll need to activate it. It can be simply done by `sourcing` the `activate` file provided by the virtual environment.

```bash
source virtualenv_name/bin/activate
```

once activated, your bash shell will be amended by the name of your virtual environment.

It's time to install all the dependencies. It can be done by using the following command.

`python3 -m pip install -r requirements.txt`

*Note - Make sure you activate your virtual environment before installing dependencies*.

Once all of these steps have been done, it's time to run the `entrypoint.sh` to *actually* `export` your variables, before you simply wrote your environment variables to a file.

Once you have done all of that, it's time to run the application, which is as simple as running the server, provided by Django itself.


`./manage.py runserver <IP>:<PORT>`

If everything goes smoothly you should see a prompt which says, `server is running at http://<host>:<port>`.

*Note - If you run into any errors or issues, feel free to raise an issue on Github (or wherever the repository is hosted) itself. You can also ask Gerard for my contact details.*

## Storage Solutions
We're using [AWS S3 Bucket] to store all of our static files, which includes, each and every CSS and JS file.

Now you must be wondering why in the world are we opting for another cloud service when we're already paying for a server? Well, it's because your server is only hosted in a particular region, let's say it's either USA or UK, or Asia. Now imagine someone from India is trying to access your web app that is hosted in UK, the time it'll take for him to load the web app fully will be increased exponentially as a literal analog signal is traveling from India to USA.

BUT if we use AWS you'll be served the static files directly from the nearest server rather than one that is 1000 KM away.

Also whenever you're deploying or updating the application on production or sandbox server you'll have to copy your static files to the AWS server, which can be done using

`./manage.py collectstatic`

This command will upload all the files to your S3 instance, regardless if it has been changed or not.

*Note - The preferred hosting solution is [Heroku]. Heroku has an empirical file system, which means everything is deleted in the file system immediately or within a given cycle, hence anything user uploads can't be kept on Heroku. AWS is used to save such files, and a path/location of the file uploaded is saved in the database itself.*

# Setting up the Production server
You can set up a production server by using any number of methods, but going by Gerard's preference we simply deploy from [Github's CI/CD], you can follow that link to learn how to set that up.

*Note - All the deployments in case of Github's CI/CD should occur from a separate branch, preferably from `release/<version>`, because the instance is refreshed every time there is a push to that branch*

## Heroku Setup
You'll need to link the concerned Github account with your application. To do this, login to the Heroku account, select an application, and you'll be greeted with a page with various options. Navigate to the "Settings" tab and scroll down a bit, you'll see a Github column there, if there's an existing Github repository (that you don't want) you'll need to unlink it.

After you're done unlinking, or in case you don't have a Github account linked at the very beginning, you'll see a "Authorize Github" button, then simply click on it, log in with your concerned account.

After you're done with that as well, in the same "Authorize Github" column, input will be available where you can enter the name of the repository you want to deploy. Once you've selected the repository, you'll be greeted with a popup where you should tick the "Automatically deploy", so whenever changes are pushed to a particular branch (you can choose the branch once you've selected the repository down below) the changes will be built and deployed.

*Note - You only have a certain number of CI/CD builds available in a day, 2000 minutes a day, which is fine but is a good thing to be cautious of, especially if you're hot patching something*


The best way of deploying on Production or Sandbox is using Docker.


# Logging and Error
We use Sentry for our logging and error detection purposes. Click here to find ["Why Sentry and not just logging?"]

It's super simple to setup sentry, just signup, and sentry will take you through the steps to setup a DNS.

# File Heirarchy
```
.
├── api
│   ├── admin.py
│   ├── apps.py
│   ├── generic
│   ├── __init__.py
│   ├── models.py
│   ├── __pycache__
│   ├── serializers.py
│   ├── staffportal
│   ├── studentportal
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── assignments
│   ├── admin.py
│   ├── apps.py
│   ├── __init__.py
│   ├── management
│   ├── migrations
│   ├── models.py
│   ├── __pycache__
│   ├── signals
│   ├── tests.py
│   └── views.py
├── contentmanager
│   ├── admin.py
│   ├── apps.py
│   ├── __init__.py
│   ├── models.py
│   ├── __pycache__
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── discoauth
│   ├── admin.py
│   ├── apps.py
│   ├── __init__.py
│   ├── migrations
│   ├── models.py
│   ├── __pycache__
│   ├── signals
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── discogportal
│   ├── asgi.py
│   ├── discostorages.py
│   ├── discoutils
│   ├── __init__.py
│   ├── __pycache__
│   ├── urls.py
│   └── wsgi.py
├── discomail
│   ├── admin.py
│   ├── apps.py
│   ├── __init__.py
│   ├── management
│   ├── migrations
│   ├── models.py
│   ├── __pycache__
│   ├── signals
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── docker-compose.yml
├── Dockerfile
├── entrypoint.sh
├── env
│   ├── prod
│   └── sandbox
├── Jenkinsfile
├── manage.py
├── module-cover-image
│   └── POC.png
├── nginx
│   ├── access.log
│   ├── Dockerfile
│   ├── error.log
│   ├── logs
│   └── nginx.conf
├── portal
│   ├── admin.py
│   ├── apps.py
│   ├── context_processor.py
│   ├── __init__.py
│   ├── models.py
│   ├── __pycache__
│   ├── staff_portal
│   ├── student_portal
│   ├── templatetags
│   ├── tests.py
│   ├── urls.py
│   └── views.py
├── Procfile
├── README.md
├── requirements
│   ├── app.txt
│   ├── heroku.txt
│   └── prod.txt
├── requirements.txt
├── runtime.txt
├── scripts
│   └── update.sh
├── settings
│   ├── base.py
│   ├── dev.py
│   ├── prod.py
│   ├── __pycache__
│   └── sandbox.py
├── static
│   ├── assets
│   ├── ckeditor
│   ├── css
│   ├── img
│   ├── js
│   └── vendors
├── templates
│   ├── 403.html
│   ├── 404.html
│   ├── 500.html
│   ├── admin
│   ├── content-manager
│   ├── dashboard
│   ├── discoauth
│   ├── discomail
│   └── student-portal
└── visualized-db-schema
    ├── 05-11-2020.png
    ├── 18-04-2020.png
    ├── 21-04-2020.png
    ├── 25-04-2020.png
    ├── 26-04-2020.png
    └── 28-04-2020.png
```

Let's go through each directory one by one.

1. `api` directory contains all the code for REST API, which is written using [Django REST Framework]. The subdirectories such as `generic`, `staffportal` etc. are app-specific API endpoints. Inside the `generic` folder there are `modelviewsets` of all the models which provide a CRUD endpoint for the concerned model.
2. `assignments` - has all the code in relation to assignments, it's also a standard Django app and the structure is standard. A `signals` directory is created to keep aside *model signals* for cleaner code.
3. `contentmanager` - has all the data and models regarding the content manager module.
4. `discoauth` - is one of the more interesting methods which holds a custom user model and all the authentication-related endpoints.
5. `discogportal` - is the central app in the project.
6. `discomail` - is used to send scheduled and un-scheduled emails.
7. `docker-compose.yml`, `Dockerfile`, `env`, `Jenkinsfile`, `nginx`, etc. are all devops related directories which help in automating deployment and serving files and configuring servers.
8. `portal` - is a standard application which holds a plethora of standard LMS related functionality.
9. `requirements` - is used to keep all the dependency related files separated by the environment, that is `app.txt` which is essential dependencies for running the application. `dev.txt` for development purposes and `prod.txt` for a production instance.
10. `settings` - holds the entirety of Django settings, depending on `DJANGO_SETTINGS_MODULE` a production or sandbox or development environment will be activated.
11. `static` - has all the CSS and JS files.
12. `templates` - has all the HTML templates related to each app sorted into separated directories with the name of the concerend app.
13. `visualize-db-schema` is a folder that holds PNG images of Db schema visualized to keep track of how the models were changed over time.





   [Django]: <https://djangoproject.com>
   [Django REST Framework]: <https://www.django-rest-framework.org/>
   [Python]: <http://python.org/>
   [Jqueyr]: <https://jquery.com/>
   ["Why Sentry and not just logging?"]: <https://sentry.io/vs/logging/>
   [Github's CI/CD]: <https://docs.github.com/en/free-pro-team@latest/actions/guides/about-continuous-integration>
   [asynchronously]: <https://bitsofco.de/asynchronous-functions-101/>
   [Postgresql]: <https://www.postgresql.org/>
   [AWS's S3 Bucket]: <https://aws.amazon.com/s3/>
   [AWS S3 Bucket]: <https://aws.amazon.com/s3/>
   [Docker image]: <https://docs.docker.com/engine/reference/commandline/image/>
   [link to install]: <https://stackoverflow.com/questions/36685980/docker-is-installed-but-docker-compose-is-not-why#:~:text=To%20install%20a%20different%20version,Compose%20you%20want%20to%20use.&text=Note%3A%20If%20the%20command%20docker,other%20directory%20in%20your%20path.>
   [Docker]: <https://docker.com>
~                                                                                                                                                                                                                                                                                                                             
