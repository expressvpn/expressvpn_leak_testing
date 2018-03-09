# ExpressVPN Leak Testing Tools

This repository contains tools built by ExpressVPN for testing how leak-proof our applications
are. The test suite is currently a work in progress and should be considered in **alpha** state.

## Note to alpha users

These tools are currently in alpha. We encourage users to independently validate the integrity of
any tests. Test results are for guidance only and should be interpreted by professional software
developers and networking engineers.

# Quick Links

For the impatient, you can jump to the following links:

* [Quick Start](docs/quick_start.md): quick start guide with limited discussion;
* [Setting Up Test Machines](docs/setting_up_test_machines.md): how to setup machines for the
  test suite.

We do, however, recommend reading [test_suite_overview.md](docs/test_suite_overview.md) to get a
feel for what the test suite consists of and how it works.

# What is this?

This repository contains a test suite built by ExpressVPN for testing VPN applications for "leaks".
(See [What Are Leaks](docs/what_are_leaks.md) for the definition of a leak.)

The test suite is mostly written in Python, with some helper tools in other languages as necessary.

The tools were initially developed as a way of unifying our leak regression tests and providing a
platform on which to build a wider range of tests. The test suite is designed with automation in
mind but also supports manual test cases for situations where automation isn't practical.

# Why Python?

We chose Python because:

* it's available on most platforms;
* code is highly portable;
* it has a broad range of libraries;
* it's familiar to a large percentage of developers;
* it allows rapid development;
* it's highly readable, allowing intents to be expressed clearly in code;

# Contact

If you have any questions regarding the tool set, please feel free to contact us and we'll try to
provide you with help or other information.

You can email us at leakproofing@expressvpn.com.

