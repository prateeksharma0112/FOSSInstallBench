## How to install

> Checkout [Grocy Desktop](https://github.com/grocy/grocy-desktop), if you want to run Grocy without having to manage a webserver just like a normal (Windows) desktop application.
>
> Directly download the [latest release](https://releases.grocy.info/latest-desktop) (also [available via the Microsoft Store](https://apps.microsoft.com/detail/9NWB1TRNNKSF)) - the installation is nothing more than just clicking 2 times "next".

Grocy is technically a pretty simple PHP application, so the basic notes to get it running are:
- Unpack the [latest release](https://releases.grocy.info/latest)
- Copy `config-dist.php` to `data/config.php` + edit to your needs
- Ensure that the `data` directory is writable
- The webserver root should point to the `public` directory
- Include `try_files $uri /index.php$is_args$query_string;` in your location block if you use nginx
  - Or disable URL rewriting (see the option `DISABLE_URL_REWRITING` in `data/config.php`)
- &rarr; Default login is user `admin` with password `admin`, please change the password immediately (user menu at the top right corner)

Alternatively clone this repository (the `release` branch always references the latest released version) and install Composer and Yarn dependencies manually.

See the website for more installation guides and troubleshooting help. &rarr; [https://grocy.info/links](https://grocy.info/links)

### Platform support

- PHP 8.5 (with SQLite 3.40+)
  - Required PHP extensions: `fileinfo`, `pdo_sqlite`, `gd`, `ctype`, `intl`, `zlib`, `mbstring`
- Recent Firefox, Chrome or Edge

## How to run using Docker

&rarr; https://hub.docker.com/r/linuxserver/grocy
