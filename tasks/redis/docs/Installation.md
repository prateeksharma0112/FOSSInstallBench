# Install Redis on Linux

How to install Redis on Linux

| Redis Open Source |
| --- |

These docs apply to Redis Community Edition and Redis Stack version 7.x.

Most major Linux distributions provide packages for Redis.

## Install on Ubuntu/Debian

Add the repository to the APT index, update it, and install Redis:

```bash
sudo apt-get install lsb-release curl gpg
curl -fsSL https://packages.redis.io/gpg | sudo gpg --dearmor -o /usr/share/keyrings/redis-archive-keyring.gpg
sudo chmod 644 /usr/share/keyrings/redis-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/redis-archive-keyring.gpg] https://packages.redis.io/deb $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/redis.list
sudo apt-get update
sudo apt-get install redis
```


Redis will start automatically, and it should restart at boot time. If Redis doesn't start across reboots, you may need to manually enable it:

```bash
sudo systemctl enable redis-server
sudo systemctl start redis-server
```


## Install on Red Hat/Rocky  [Copy link to clipboard](https://redis.io/docs/latest/operate/oss_and_stack/install/archive/install-redis/install-redis-on-linux/\#install-on-red-hatrocky "Copy link to clipboard")

```bash
sudo yum install redis
sudo systemctl enable redis
sudo systemctl start redis
```


Redis will restart at boot time.

## Install on Ubuntu using Snap  [Copy link to clipboard](https://redis.io/docs/latest/operate/oss_and_stack/install/archive/install-redis/install-redis-on-linux/\#install-on-ubuntu-using-snap "Copy link to clipboard")

To install via Snap, run:

```bash
sudo apt update
sudo apt install redis-tools # for redis-cli
sudo snap install redis
```


Redis will start automatically, but it won't restart at boot time. To do this, run:

```bash
sudo snap set redis service.start=true
```



You can use these additional snap-related commands to start, stop, restart, and check the status of Redis:

- `sudo snap start redis`
- `sudo snap stop redis`
- `sudo snap restart redis`
- `sudo snap services redis`

If your Linux distribution does not currently have Snap installed, you can install it using the instructions described [here](https://snapcraft.io/docs/installing-snapd). Then, consult the [Snapcraft store](https://snapcraft.io/redis) for instructions on installing Redis using Snap for your distribution.

## Starting and stopping Redis in the background

You can start the Redis server as a background process using the `systemctl` command. This only applies to Ubuntu/Debian when installed using `apt`, and Red Hat/Rocky when installed using `yum`.

```bash
sudo systemctl start <redis-service-name> # redis or redis-server depending on platform
```



To stop the server, use:

```bash
sudo systemctl stop <redis-service-name> # redis or redis-server depending on platform
```



## Connect to Redis

Once Redis is running, you can test it by running `redis-cli`:

```bash
redis-cli
```


Test the connection with the `ping` command:

```bash
127.0.0.1:6379> ping
PONG
```

You can also test that your Redis server is running using
[Redis Insight](https://redis.io/docs/latest/develop/tools/insight/).

