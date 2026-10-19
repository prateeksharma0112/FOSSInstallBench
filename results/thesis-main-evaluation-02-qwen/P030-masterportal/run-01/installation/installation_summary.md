## Method used (per Installation.md quick-start)

1. **Download last stable version**: `curl -sL -o /workspace/examples.zip https://bitbucket.org/geowerkstatt-hamburg/masterportal/downloads/examples.zip` (7,019,648 bytes; 201 entries containing `basic/` and `mastercode/3_27_1/`).
2. **Install a web server**: Installed Apache 2 via `apt-get install -y apache2` (Ubuntu 22.04.5 container, running as root; `unzip` was also installed).
3. **Publish under htdocs**: Extracted the archive to `/var/www/html/examples/` (Apache document root), yielding `/var/www/html/examples/basic/` and `/var/www/html/examples/mastercode/3_27_1/{css,img,js,locales}`.
4. **Name alignment**: The guide expects the example folder `Basic`, while the zip ships it as lowercase `basic` (referenced by `index.html` via relative paths). Created symlink `/var/www/html/examples/Basic -> basic` so the guide's URL works verbatim.
5. **Start the server**: `service apache2 start` (container has no systemd; init.d service script used). Apache reports "apache2 is running", listening on port 80.

## Resulting state / access points

- Portal URL per guide: `http://<server>/examples/Basic/index.html` (locally: `http://localhost/examples/Basic/index.html`)
- Also reachable at `http://localhost/examples/basic/index.html`
- Deployment root: `/var/www/html/examples/` — 201 entries (177 files + 24 dirs) exactly matching the zip manifest, verified by `comm` diff
- Config files: `/var/www/html/examples/basic/config.js`, `config.json`; global configs in `/var/www/html/examples/basic/resources/{services.json,rest-services.json,style_v3.json}`
- Masterportal code: `/var/www/html/examples/mastercode/3_27_1/` (version 3.27.1 of the released mastercode)
- Downloaded artifact kept at `/workspace/examples.zip`

## Notes

- The repository checked out in `/workspace` is the Masterportal source (v3.26.1, commit 410dc25); per the guide the installation is done from the prebuilt Bitbucket examples download, not from the source build.
- Custom-portal steps from the guide (duplicating `basic` into a renamed portal folder) were not performed since the task is to install and make the example application available.