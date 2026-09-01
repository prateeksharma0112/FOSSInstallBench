# Leantime

### ️⚡️ Installation (Production) ###

There are two main ways to install LeanTime for production. The first of which is to install all needed pieces of the system locally. The second is to use the officially supported Docker image.

#### Local Production Installation ####

* Download latest release package (file is called: Leantime-vx.x.x.zip) from the <a href="https://github.com/Leantime/leantime/releases">release page</a>
* Create an empty MySQL database
* Upload the entire directory to your server 
* Point your domain root to the `public/` directory
* Rename `config/sample.env` to `config/.env`
* Fill in your database credentials (username, password, host, dbname) in `config/.env`
* Navigate to `<yourdomain.com>/install`
* Follow instructions to install database and set up first user account

##### IIS Installation Notes #####

Whilst the steps above are applicable to Internet Information Services (IIS), there is an additional configuration change that may be required in IIS to ensure full functionality - you need to allow the PATCH method:

* Open IIS
* Expand the server and sites on the left and select the LeanTime site
* Double click on `Handler Mappings`
* Double click on the PHP handler mapping that is used by the site
* Click `Request Restrictions…`
* Click the `Verbs` tab
* In the `One of the following verbs` text box, add `PATCH` - for example: `GET,HEAD,POST,PATCH`
* Click `OK`
* In the `Executable (optional)` text box, put a double quote character (`“`) at the start and at the end of the path to the `php-cgi.exe` file (_this isn't needed if the path doesn't have a space in it_)
* Click `OK`
* A popup will appear asking if you want to create a FastCGI application - click `Yes`

Note: You may need to repeat this when you upgrade PHP.

#### Production Installation via Docker ####

We maintain an official <a href="https://hub.docker.com/r/leantime/leantime">Docker image on dockerhub</a>. 
To run the image enter your MySQL credentials and execute. You can pass in all the configuration variables from .env

```
docker run -d --restart unless-stopped -p 8080:8080 --network leantime-net \
-e LEAN_DB_HOST=mysql_leantime \
-e LEAN_DB_USER=admin \
-e LEAN_DB_PASSWORD=321.qwerty \
-e LEAN_DB_DATABASE=leantime \
-e LEAN_EMAIL_RETURN=changeme@local.local \
--name leantime leantime/leantime:latest
```

Unless you have a database defined somewhere else you should use our [docker-compose file](https://github.com/Leantime/docker-leantime/blob/master/docker-compose.yml). 

Once started you can go to `<yourdomain.com>/install` and run the installation script.

**Important: If you are planning to use plugins you need to mount the plugin folder `plugins:/var/www/html/app/Plugins` and ensure the www-data user has access to it. Otherwise installation may fail or plugins will be removed after a restart**

##### Docker Installation Notes #####

If you intend to place Leantime behind a reverse proxy (nginx, etc.) to handle custom domain name resolution and SSL offloading, you will need to set the following environment variable in docker
```
-e LEAN_APP_URL=https://yourdomain.com \
```
* Update yourdomain.com to your custom domain name.
<br /><br />
### 🤓 Installation (Development) ###

There are two ways to install a development setup of LeanTime. The first (but most technical) is to install all pieces of the system locally. The second (and preferred method) is to use a docker containerized development environment.

#### Local Development Installation ####

* Clone repository to your local server
* Create MySQL database
* Run webpack builder via `make build-dev`
* Point your local domain to the `public/` directory
* Rename `config/sample.env` to `config/.env`
* Fill in your database credentials (username, password, host, dbname) in `config/.env`
* Navigate to `<localdomain>/install`
* Follow instructions to install database and user account

#### Development Installation via Docker ####

For development, we use a dockerized development environment. You will need to have ``docker``, ``docker compose``, ``make``, ``composer``, ``git`` and ``npm`` installed.

* Notes for Windows Environments:
    - Run all commands within the git bash terminal in order to utilize unix specific commands
    - If installing php from a zip file, make sure to configure php.ini
    It does not exist initially, so copy C:\php\php.ini-development to C:\php\php.ini. You will also need to edit php.ini in a text editor and enable all needed extensions for the build process. You can find these by running the make commands and looking for any extensions that error out as missing. You can enable them by searching php.ini for the extension that will look like: `;extension=gd` and removing the semicolon. 

In order to build the development docker image, in the root of this repository, run a primer with

```make clean build```

afterwards, run 

```make run-dev```

this will start the development server on port 5080.

The dev environment provides a MySQL server, mail server, s3 server, and should be good to go for your needs out of the box. The basic configuration of the development environment is already defined in the composer file. You can create .env file inside of `config/.env` to augment the base configuration by setting some of the configs out of sample.env). **Important: Don't update the database information as this will disconnect the app from the docker database**. The applications you get are as follows

* [http://localhost:5080](http://localhost:5080) : leantime
* [http://localhost:8081](http://localhost:8081) : maildev - to check emails sent
* [http://localhost:8082](http://localhost:8082) : phpMyAdmin(authentication ``leantime:leantime``) to check the DB schema and data
* [http://localhost:8083](http://localhost:8083) : s3ninja - to check s3 uploads. You need to enable this in the ``.dev/.env`` file by enabling s3

Additionally, Xdebug is enabled, but you will have to modify your 
IDE key in the ``.dev/xdebug.ini`` file(or alternatively, on your IDE). You also need to have port 9003 temporarily open on your firewall so you can utilize it effectively. This is because connections from docker to the host will count as external inbound connections
<br /><br />

### Run Tests

Static Analysis `make phpstan`<br />
Code Style `make test-code-style` (to fix code style automatically use `make fix-code-style`)<br />
Unit Tests `make unit-test`<br />
Acceptance Tests `make acceptance-test`<br /> (requires docker)

You can test individual acceptance test groups directly using:<br />
For api: <br />
`docker compose --file .dev/docker-compose.yaml --file .dev/docker-compose.tests.yaml exec leantime-dev php vendor/bin/codecept run -g api --steps`<br />
For timesheets: <br />
`docker compose --file .dev/docker-compose.yaml --file .dev/docker-compose.tests.yaml exec leantime-dev php vendor/bin/codecept run -g timesheet --steps`<br />
