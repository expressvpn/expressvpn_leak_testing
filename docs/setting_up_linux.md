# Linux

## Install packages

### Ubuntu

```
sudo apt-get install python3-dev libdbus-glib-1-dev
```

### Fedora

```
sudo dnf install redhat-lsb-core python3-devel gcc dbus-devel dbus-glib-devel
```

## Checkout xv\_leak\_tools\_internal

Simply `git clone` this repo to a location of your choice. We'll refer to the `python` subfolder in
that location as `$LEAK_TOOLS_ROOT`.

## Setup Python

Run `./setup_python.sh $VIRTUALENV_LOCATION` where `$VIRTUALENV_LOCATION` is the directory
where you want the virtualenv to be created, e.g.

```
./setup_python.sh ~/xv_leak_testing_python
```

You can now source the `activate` script as a shortcut to activating `virtualenv` with this version
of python.

## Install VPN Applications

Install ExpressVPN and any other applications you want to test. No specific steps related to leak
testing are required.

## Install Browsers and Webdrivers

First ensure that Chrome, Firefox and Opera are installed (where supported).

> Note that some drives can be installed with package managers, e.g. apt.

In order for selenium to control various browsers some install steps are required.

Install Edge driver: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/#downloads

Install Chrome driver: https://chromedriver.storage.googleapis.com/index.html?path=2.30/

Firefox gecko driver: https://github.com/mozilla/geckodriver/releases

Opera driver: https://github.com/operasoftware/operachromiumdriver/releases

## Install Torrent Clients

You can choose which torrent clients you want to test. We have tested

* Transmission
* uTorrent
