# Windows

> We currently only support cygwin as the shell which the test suite can run in. Support for DOS
  or other shells may be considered later on.

> The tests are designed to run on x86-64. If you're running a 32-bit OS, see [Troubleshooting](#troubleshooting) below.

On Windows you need to make several executables available to the leak tools. Currently the best way
of doing this is to create a folder somewhere and add it to the `PATH` environment variable for your
user. Then just dump binaries into this folder as needed. We refer to this as `EXTRA_BIN_PATH` from
here on in.

Examples include Windump.exe, chromedriver.exe. These are standalone binaries with no installers.

> TODO: We should add a bin path to the tool suite for convenience.

## Setup Cygwin

* Install Cygwin as per the instructions in https://www.cygwin.com/install.html.
  * Ensure you install `lynx` web client package.
* Install `apt-cyg` (as per the instruction in https://github.com/transcode-open/apt-cyg):
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
> `procps-ng` gives you `watch` which can be useful.

## Checkout

Simply `git clone` this repo to a location of your choice. We'll refer to the `python` subfolder in
that location as `$LEAK_TOOLS_ROOT`.

## Configure SSH

Optional for now. Only require if you want to run the tests remotely on the Windows machine.

> TODO: Explain how

## Setup python

Run `./setup_python.sh $VIRTUALENV_LOCATION` where `$VIRTUALENV_LOCATION` is the directory
that you want the virtualenv to be created in, e.g.

```
./setup_python.sh ~/xv_leak_testing_python
```
> TROUBLESHOOTING: If the error `Failed building wheel for ...` occurs,
  * reboot and ensure there are no cygwin processes running;
  * run `C:\cygwin64\bin\ash` as an administrator;
  * run `/bin/rebaseall`.
  If the issue persists, rebase again and reinstall Python from the cygwin executable.

You can now source the `activate` script as a shortcut to activating `virtualenv` with this version
of Python.

## Configure `EXTRA_BIN_PATH`

Make a directory wherever you like and add it to your `PATH` (e.g. `C:\Program Files (x86)\xv_leak_test`).
To add directories to the `PATH`, open `Control Panel` > `System` > `Advanced system settings` >
`Environment Variables…` > `PATH`.

## Install capture tools

Install winpcap from https://www.winpcap.org/.

Download Windump from https://www.winpcap.org/windump/ and copy it into `$EXTRA_BIN_PATH`.

## Install helper tools

> ❗️WARNING: These tools were previously dependent on a 3rd party application called `windows-kill`.
  The GitHub repo for that tool has recently been taken over. We have removed the link to the repo
  as a security precaution. If you wish to run the tools on Windows then, as of the time of writing,
  you will either need to find an alternative distribution of the source/binaries for this tool or
  find a suitable replacement.

Download pre-built binaries of `windows-kill` or build them yourselves. Then copy the binaries into
`$EXTRA_BIN_PATH`.

## (Optional) Setup cmder

cmder is probably the best shell on Windows. It can easily be configured to use the cygwin
environment and thus act as a shell wrapper around cygwin.

Setup instructions for cmder can be found at http://cmder.net/.

For details on how to integrate cmder with cygwin, see
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

You can choose which torrent clients you want to test. We have tested:

* Transmission,
* uTorrent.

## Troubleshooting

### `Subprocess execution failed: cmd: ['run', '"/cygdrive/c/Program Files (x86)/ExpressVPN/xvpn-ui/ExpressVpn.exe"']`

This occurs when the test machine is a 32-bit Windows OS. The solution is to create `C:/Program Files (x86)/`
and symlink the ExpressVPN directory into it with
`mklink /J "C:\Program Files (x86)\ExpressVPN" "C:\Program Files\ExpressVPN"` (not in a cygwin shell).
