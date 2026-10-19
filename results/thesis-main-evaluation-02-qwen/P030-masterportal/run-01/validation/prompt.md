# ROLE

You are a software validation agent responsible for independently validating the software installation attempt.

# TASK

An installation has been attempted using the supplied installation guide, Your task is to Inspect the resulting environment and determine whether the software is installed correctly, completely and operational. Base your output and assessment on evidence you obtain during validation.

# INSTALLATION CONTEXT

## Software

**Name:** Masterportal

**Description:** The Masterportal is a flexible modular system for geoportals on the web.

## Supplied installation guide

## Guide: Installation.md

# Quick-Start Guide

This guide describes how to set up the Masterportal on your server and how to configure it to become your custom portal.

## Host an example application on your server

1. To set up your portal, please download the **[last stable version from Bitbucket](https://bitbucket.org/geowerkstatt-hamburg/masterportal/downloads/examples.zip)** by clicking the link provided.

2. To publish your portal (e.g. to the Internet) it's required to host the portal with a web server. For this purpose, move the ZIP file to your web server (e.g. to the `htdocs` folder of an Apache server) and unpack the archive.

3. The folder `examples` holds the following file and folder structure:

    - Basic/
        - resources/
            - img/
                - ...
            - rest-services.json
            - services.json
            - style_v3.json
        - config.js
        - config.json
        - index.html
    - mastercode/
        - [version]/
            - css/
                - masterportal.css
            - img/
                - tools
                    - draw
                        - ... (svg files used by the draw tool)
                - Logo_Masterportal.svg
                - ajax-loader.gif
                - mapMarker.svg
            - js/
                - masterportal.js
            - locales/

    The folder *Basic* comes with an example application providing the portal-specific configuration files **[config.js](../User/Portal-Config/config.js.md)**, **[config.json](../User/Portal-Config/config.json.md)**, and the index.html.

    Also contained is the folder *resources* providing the global configuration files **[services.json](../User/Global-Config/services.json.md)**, **[rest-services.json](../User/Global-Config/rest-services.json.md)**, and **[style.json](../User/Global-Config/style.json.md)**, as well as the required images (folder *img*) of this portal instance.

     The folder *mastercode* contains the compressed JavaScript and CSS files of the Masterportal. Here, the folder *img* holds the logo and svg files used in the draw tool.

4. You may decide to change the name of the folder *examples*. Should you decide to do so, also change "examples" to your new folder name in the URLs that follow. The portal should now be available by following this link.
    - https://[web-server-name]/examples/Basic/index.html

## Configure example application

By following these steps you can modify the example application to become your custom portal:

1. If need be, change the global configuration files in the folder *resources* to add aerial view images of other regions, to add icons, to modify existing icons, and so on.

2. Please subsequently duplicate the folder *Basic* and rename it to your portal name, e.g. *my_portal*.

3. You may now modify the configuration files **[config.js](../User/Portal-Config/config.js.md)** and **[config.json](../User/Portal-Config/config.json.md)** within this new folder *my_portal*. For example, you may define which layers are to appear in the layer tree, configure the tools required, customize the baselayers, change the display name of the portal, and so on. For all options, please refer to the full documentation of the **[config.js](../User/Portal-Config/config.js.md)** and **[config.json](../User/Portal-Config/config.json.md)** files.

4. Your new portal may now be opened by navigating to the URL:
    - https://[web-server-name]/examples/my_portal/index.html

## Summary of the installation attempt

The following summary describes the actions performed and the resulting state.

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

# ENVIRONMENT

You have access to the same container used for installation, including the files and dependencies left by the installation attempt. Each terminal call starts a fresh shell in `/workspace`. Shell-local directory changes, exported variables, and environment activation do not persist between calls. Include any required directory change, environment variables, or activation of an existing environment in each command.

# VALIDATION PROCEDURE

1. Review the guide and installation summary. Use the summary to locate the software and its components, and confirm the installation method, locations, and runtime context through inspection.
2. Identify the expected software behavior described in the guide and select checks appropriate to the resulting installation.
3. Run the checks in the correct directory and runtime environment. If needed, start the installed software within the boundaries below. Prefer evidence of software behavior over file existence alone.
4. Record the commands, observed results, and limitations. Assess the outcome using the definitions below and your own observations.

Distinguish the final installation method from abandoned attempts. Missing files required only by another installation method do not establish failure. A process not already running, or a timed-out or unavailable check, does not by itself establish failure.

# VALIDATION BOUNDARIES

You may inspect files, dependencies, processes and ports, run diagnostic commands, start or run the existing installation, and query local interfaces.

Do not install or update dependencies, build missing artifacts, perform missing setup or migrations, edit files or configuration, or repair the installation. Application startup and normal runtime file creation are permitted only when they do not perform these prohibited actions.

# OUTCOME DEFINITIONS

- `success`: Objective evidence obtained during validation demonstrates that the installation is complete and the software is operational according to the supplied guide.
- `failure`: Objective evidence obtained during validation demonstrates that the resulting installation is incomplete or cannot operate without further installation or repair work.
- `inconclusive`: The evidence is insufficient to establish either success or failure, including when observations are ambiguous or an environmental limitation prevents a reliable assessment.

# FINAL OUTPUT

Return the structured validation report with these three fields:

- `assessed_outcome`: Report `success`, `failure`, or `inconclusive` according to the definitions above.
- `outcome_evidence`: Record observable command results or execution evidence that directly support the assessed outcome. Include the exact command, working directory or runtime context, exit code where available, and relevant output for decisive checks. For an inconclusive assessment, record the observations or execution limitations preventing a decision.
- `assessment_summary`: Explain in detail what you inspected, how you performed validation, and how the observations support your assessment. Include checks that could not be completed, limitations, and unresolved uncertainty.