## Quickstart

You can quickly try the online demo with restricted access, login credentials are `smartcity:smartcity`:

[Online demo](https://demo.openremote.app/manager/?realm=smartcity)

The quickest way to get your own environment with full access is to make use of our docker images (both `amd64` and `arm64` are supported).

1. Make sure you have [Docker Desktop](https://www.docker.com/products/docker-desktop) installed (v18+).
2. Download the docker compose file:
   [OpenRemote Stack](https://raw.githubusercontent.com/openremote/openremote/master/docker-compose.yml) (Right click 'Save link as...')
3. In a terminal `cd` to where you just saved the compose file and then run:

```
docker compose pull
docker compose -p openremote up
```

If all goes well then you should now be able to access the OpenRemote Manager UI at [https://localhost](https://localhost). You will need to accept the self-signed
certificate, see [here](https://www.technipages.com/google-chrome-bypass-your-connection-is-not-private-message) for details how to do this in Chrome (similar for other browsers).

### Login credentials

Username: admin  
Password: secret

### Changing host and/or port

The URL you use to access the system is important, the default is configured as `https://localhost` if you are using a VM then you will need to set the `OR_HOSTNAME` environment variable, so if for example you will be accessing using `https://192.168.1.1` then use the following startup command:

BASH:

```shell
OR_HOSTNAME=192.168.1.1 docker-compose -p openremote up -d
```

or

CMD:

```shell
cmd /C "set OR_HOSTNAME=192.168.1.1 && docker-compose -p openremote up -d"
```
