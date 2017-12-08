# Quick Start

We only focus on "single machine tests" in the Quick Start guide. That is, tests which can run
entirely on your local device. Some more advanced tests cases require multiple machines networked
together, e.g. a mobile device, a router device, a port spanning switch and a desktop device for
collection spanned traffic.

See TODO for more details on multi-machine tests

The test suite must always be run from a desktop device. We refer to this device as the "Test
Orchestrator". For single machine tests, the Test Orchestrator is actually the device under test.

## Decide whether you want to work with a VM

VMs provide more flexibility with regards to network configurations. It's much easier to configure
multiple adapters, capture traffic from the guest, firewall the guests network. For the purpose
of a "quick start" you should only need a VM if:

* You can't provide a local DNS server to your device
  * Some test cases require a local DNS server
  * You can fail to have one if, for example, your network is specifying public DNS servers via
    DHCP, e.g. 8.8.8.8.
  * Using a NAT'd network adapter for the VM guest will give you a local DNS server.

## Setup Your Machine

First follow [Setting Up Test Machines](docs/setting_up_test_machines.md) for you machine of
choice. We recommend using MacOS for quick start.

## Run Some Tests

To run a bunch of tests do the following

* Pick a config file (`$CONFIG_FILE`)
  * We recommend starting with `configs/auto/template_desktop_generic_tests_localhost.py`.
* Create an output directory somewhere (`$OUTPUT`).
* Open a shell and execute:
  * `./run_tests.sh -o $OUTPUT -c $CONFIG_FILE`

All tests currently require root (or admin) to run. The suite is designed to facilitate running
non-root tests, however currently most tests require root is some way or other. The suite will
ask you for root permission when it needs it.

> You should ensure that none of the test suite files are owned by root. You should never need to be
  in a root shell at any time. Just rely on the tests asking you for root when they need it.

The test framework will output lots of information to the console. The default log level is INFO and
should be sufficient for quick start. However, if you wish to up the level then use the `-l`
parameter.

The types of logging you will see are:

* `INFO`: Useful information about the progress of the test.
* `WARNING`: No fatal issues. Shouldn't require action for quick start.
* `ERROR`: Fatal test failures. These will either be due to explicit failure of a test assertion or
  due to the test framework throwing an exception.
* `DESCRIBE`: Each describe output specifies a repro step for the test. When put together they
  should read like a bullet point list of how to manually reproduce the steps. These steps are
  all collected together in a file in the output folder for the test for convenience.
* `INTERACTIVE`: This indicates steps which require manual interaction. The test will display some
  information about what steps to take and pause whilst those steps are taken, e.g.

```
2017-11-17 08:57:41,425 INTERACTIVE:
Connect to the VPN
Press ENTER to continue...
```

> See TODO on how to fully automate tests.

You should see the test framework execute a set of tests and report whether each one succeeded or
failed.

We discuss test execution in detail in TODO.

## Structure of Test Suite

Everything here is covered in full detail in [Test Suite Overview](test_suite_overview.md).

### Test Cases

This repo contains many test cases. They can mostly be found in the `desktop_local_tests` folder.
A test case is any python class which

* Derives from `TestCase`
* Whose name begins with `Test`

> Test classes must have unique names - you will get an error if they don't.

A test case requires a configuration to run. The configuration specifies:

* What devices the test will use to run
* The configuration of the device
* Parameters for the test
  * Some tests can execute in different ways when different parameters are passed.

Configurations are passed to the test suite via the `-c` argument to `run_tests.sh`. The value of
this argument should be a python file which exposes an attribute `TESTS` - which should be a list
of dictionaries.

Each dictionary is a configuration for a specific test. It tells the test suite to run that test
once with the particular settings.

> Tests can live in any folder. Extra folders can be specified via the `Test Run Context`. See
  TODO for more information.

### Test Configs

We discuss test configurations in detail in TODO.

### Test Devices

Devices are identified using inventory files. Inventory files can live anywhere. There is an example
inventory in the `devices` directory. Inventory files are python files which expose an attribute
`DEVICES` - which should be a list of dictionaries.

Each dictionary specify a known device in your inventory. This may be a physical device or a VM.

If no device inventory is specified when tests are run, then the only device available will be your
local device on which you run the tests suite. This is made available via the `localhost` device ID.

> For the purpose of "quick start" localhost will be adequate and no additional configuration should
  be necessary, i.e. no device inventory should be needed.

The framework has been designed to be very generic. It caters for test cases which need multiple
devices networked together. Device inventories are used to list all currently available devices to
the test orchestrator. Some tests may not use the local device at all except for orchestrating the
test runs themselves.

We discuss devices in detail in TODO.

### The Test Suite

All test suite code is under the `xv_leak_tools` folder.

Test execution begins with `xv_leak_tools/test_execution/test_runner.py`. Test execution requires a
`TestRunContext` object which is used to parameterize the test framework itself. The wrapper script
`/tools/run_tests.py` will process command line arguments and ensure that the test suite is passed:

* A test output directory
* A test run context
* A list of test configs
* A device inventory

The real entry point for the test suite is in `xv_leak_tools/test_execution/test_runner.py`, which
receives the above objects from `run_tests.py`.

> Note that there's an additional higher level wrapper shell script `run_tests.sh` which should be
  used to run `/tools/run_tests.py`. This is just a helper script to ensure the suite can be
  run in a platform agnostic way.

When the test suite runs, it roughly does the following

* Discovers all available test cases (classes deriving from `TestCase`)
* Iterating through each test configuration
* Create an instance of the test case class for the test
* Finds the devices specified in the test config but looking through the device inventory
* Creates "connections" - roughly speaking, SSH connections - to all devices
* Runs the tests, including
    * Setup and teardown
    * Handling success/failure
    * Handling exceptions.

The test runner will tell you what went wrong and summarise failures. It's similar to most unit
testing frameworks but tailored to leak testing.

### Where to go next?

* Learn about the current test cases: TODO
* Learn about building your own configurations: TODO
* Learn about creating device inventories: TODO
