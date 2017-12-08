# Test Suite Overview

## Test Cases vs Test Configurations

Inside this repository are many test cases which test scenarios under which VPNs may leak. The tests
cases are designed to be agnostic to almost everything, for example they do not care about:

* Which VPN application is being tested
* What devices are being used in the test
* Which version of the OS is being used
  * In some cases even *which* OS is being used
* What network configuration the device has
* Which browser is used for tests with browsers
* Which torrent client is used for tests with torrent clients

If you wish to test a particular combination of settings then this is achieved by providing a test
configuration and a device configuration. The combination of the two allow the same test to be run
under many different setups.

## Automation vs Manual Interaction

Our goal in writing this suite is to make as many test cases as possible fully automated. In many
cases this can be tricky or even impossible (within reason). The compromise for many tests is
that manual steps are required in order to fully complete the test scenario.

One of the hardest parts of automation is automating the control of the VPN application. Currently
this test suite does not include any code for automating control of the VPN applications. Any test
steps which require manipulating the VPN application - such as connecting, disconnecting or
configuring the VPN application - will prompt the user to manually perform that step.

Internally we have automated control of our own application for the purposes of regression testing.
We currently don't plan to ship the tools we use to automatically control our application thus if
you run this test suite against our application the tests will default to asking for manual
interaction.

The test suite is however designed so that automation of the VPN application (or in fact any
component) can be added without the need to change the tests, test configurations, devices etc..
Indeed this is how we use the suite internally by providing our own overrides to the VPN
application.

For desktop tests, aside from VPN application control, most of the test steps are automated. For
example:

* Changing network configurations
* Making DNS requests
* Generating general IP traffic
* Visiting webpages

For mobile tests much has yet to be automated. In some extreme cases, all the tests steps are
currently manual. However, having such tests cases still has many benefits:

* Test cases clearly document scenarios where we consider a risk of leaking
* Test steps are clearly documented like QA repro steps
* Running such tests is still faster than manually running tests
* Running such tests is far less error prone than manually running tests
* Tests can be run by third parties without requiring lengthy ramp-ups

We plan to increase the amount of automation over time and also document how we setup our devices
in more complex scenarios to aid in the automation of tests.
