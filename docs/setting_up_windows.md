# Windows

> We currently only support cygwin as the shell which the test suite can run in. Support for DOS
  or other shells may be considered later on.

On windows you need to make several executables available to the leak tools. Currently the best way
of doing this is to create a folder somewhere and add it to the `PATH` environment variable for your
user. Then just dump binaries into this folder as needed. We refer to this as `EXTRA_BIN_PATH` from
here on in.

Examples include Windump.exe, chromedriver.exe. These are standalone binaries with no installers.

> TODO: We should add a bin path to the tool suite for convenience.

## Setup Cygwin

* Install Cygwin as per the instructions here: http://www.cygwin.com/install.html
** Ensure you install `lynx` web client package
* Install `apt-cyg` (as per the instruction here: https://github.com/transcode-open/apt-cyg):
```
lynx -source rawgit.com/transcode-open/apt-cyg/master/apt-cyg > apt-cyg
install apt-cyg /bin
```
* Install the following packages:
```
apt-cyg install git python3 python3-devel libffi-devel openssl-devel make bind-utils gcc-g++ curl
```
* (Optional) Other useful packages:
```
apt-cyg install procps-ng vim
```
> `procps-ng` gives you `watch` which can be useful

## Checkout xv\_leak\_tools\_internal

Simply `git clone` this repo to a location of your choice. We'll refer to the `python` subfolder in
that location as `$LEAK_TOOLS_ROOT`.

## Configure SSH

Optional for now. Only require if you want to run the tests remotely on the Windows machine.

> TODO: Explain how

## Setup python

Run `./setup_python.sh $VIRTUALENV_LOCATION` where `$VIRTUALENV_LOCATION` is the directory
where you want the virtualenv to be created, e.g.

```
./setup_python.sh ~/xv_leak_testing_python
```

You can now source the `activate` script as a shortcut to activating `virtualenv` with this version
of python.

## Install capture tools

Install libpcap from here: https://www.winpcap.org/

Download Windump from here: https://www.winpcap.org/windump/ and copy it into `EXTRA_BIN_PATH`.

## Install helper tools

Download pre-built binaries of https://github.com/alirdn/windows-kill or build them yourselves. Then
copy the binaries into `EXTRA_BIN_PATH`.

## (Optional) Setup cmder

> WARNING: cmder isn't a great idea just yet. There's a problem with running `xv_toolbox` commands
  automatically with cmder. It causes execution to halt due to a shell window not closing. Just
  use cygwin for now and ignore cmder.

We recommend cmder as the best shell on Windows. This can easily be configured to use the cygwin
environment and thus acts as a shell wrapper around cygwin.

Setup instructions for cmder can be found here: http://cmder.net/.

For details on how to integrate cmder with cygwin see here:
https://github.com/cmderdev/cmder/wiki/%5BWindows%5D-Integrating-Cygwin.

> Note that a missing step in that setup guide is to go to "Startup" and set your newly created task
  as the "Specified named task".

## Install VPN Applications

Install ExpressVPN and any other applications you want to test. No specific steps related to leak
testing are required.

## Install Browsers and Webdrivers

First ensure that Chrome, Firefox, Opera and Edge are installed.

> TODO. Might not test IE.

In order for selenium to control various browsers some install steps are required.

Install Edge driver: https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/#downloads

Install Chrome driver: https://chromedriver.storage.googleapis.com/index.html?path=2.30/

Firefox gecko driver: https://github.com/mozilla/geckodriver/releases

Opera driver: https://github.com/operasoftware/operachromiumdriver/releases

## Install Torrent Clients

You can choose which torrent clients you want to test. We have tested

* Transmission
* uTorrent
