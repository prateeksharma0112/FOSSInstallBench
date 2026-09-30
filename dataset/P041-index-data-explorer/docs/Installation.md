## Installation

#### Basic idea

The _Index Data Explorer_ is a web application, written in HTML and Javascript. So everything you need on the endusers computer is a modern web browser (like e.g. Firefox or Chromium)

##### Prerequisites:
 - WebServer (linke e.g. Apache or Nginx)
 - Elasticsearch Service
 
##### Steps:
 - Add the following folders from toplevel of the project to the document root folder of the webserver or a subdirectory of your choice:
   + config
   + externalPackages
   + i18n
   + src
   + php (* only needed, if the computer running the browser has no acccess to the used Elasticsearch service *)
   + Additionally you need a folder _data_ on toplevel for specific instances, e.g. for some pages in _examples/kosis_
 - copy the HTML pages you want to offer in _your_ Explorer instance to the same folder of the webserver
 - Note: all the HTML pages on toplevel or in one of the folders in subfolder _examples_ can be copied to the document root folder and are functional there (that is: will find their used/imported files like CSS or images or configuration files)
 - Note: check the _examples_ directory to see some proper use cases
 - Adjust the values in the config files used by your HTML pages to the correct index name(s) and base URL. Additionally you can overwrite the default configurations of most javascript modules found in subfolder _src_ in the config files.

For more detailed information refer to the wiki page mentioned above.
