# MacOS

## Homebrew

* Install homebrew: https://brew.sh/
* `brew install python3 geckodriver chromedriver`

## Checkout xv\_leak\_tools\_internal

Simply `git clone` this repo to a location of your choice. We'll refer to the `python` subfolder in
that location as `$LEAK_TOOLS_ROOT`.

## Setup python

Run

* `python3 -m ensurepip`
* `pip3 install virtualenv`

Run `./setup_python.sh $VIRTUALENV_LOCATION` where `$VIRTUALENV_LOCATION` is the directory where you
want the virtualenv to be created, e.g.

```
./setup_python.sh ~/xv_leak_testing_python
```

You can now source the `activate` script as a shortcut to activating `virtualenv` with this version
of python.

> TODO: Consider adding pyobjc directly into the codebase. It looks like it's not updated often.

## Install VPN Applications

Install ExpressVPN and any other applications you want to test. No specific steps related to leak
testing are required.

## Install Browsers and Webdrivers

Ensure that Chrome, Firefox, Opera and Safari are installed.

In order for selenium to control various browsers some extra steps are required.

> Note that Chrome and Firefox are covered by the `brew` steps above.

### Opera

You need to copy the opera driver into a folder in your `PATH` variable. It can be downloaded from
https://github.com/operasoftware/operachromiumdriver/releases. The easiest thing to do is just copy
it into `/usr/local/sbin`.

### Safari

Safari doesn't need an extra driver, but permissions are required to drive the browser. Go to
Safari->Preferences->Advanced and check "Show Develop in Menu Bar". Then go to the Develop dropdown
in the menu bar and check "Allow Remote Automation".

## Install Torrent Clients

You can choose which torrent clients you want to test. We have tested

* Transmission
* uTorrent
