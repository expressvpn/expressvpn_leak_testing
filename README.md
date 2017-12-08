# ExpressVPN Leak Testing Tools

This repository contains tools built by ExpressVPN for testing the how leak-proof our applications
are. The test suite is currently a work in progress and should be considered in **alpha** state.

# Quick Links

For the impatient, you can jump to the following links:

* [Quick Start](docs/quick_start.md): Quick start guide with limited discussion
* [Setting Up Test Machines](docs/setting_up_test_machines.md): How to setup machines for the
  test suite

We do however recommend reading [test_suite_overview.md](docs/test_suite_overview.md) to get a feel
for what the test suite consists of and how it works.

# What is this?

This repository contains a test suite built by ExpressVPN for testing VPN applications for "leaks"
(see [What Are Leaks](docs/what_are_leaks.md) for the definition of a leak).

The test suite is mostly written in python, with some helper tools in other languages as necessary.

The tools were initially developed as a way of unifying our leak regression tests and providing a
platform on which to build a wider range of tests. The test suite is designed with automation in
mind but also supports manual test cases for situations where automation isn't practical.

They tools have since grown into a

# Why Python?

We chose python because:

* It's available on most platforms
* Code is highly portable
* It has a broad range of libraries
* It's familiar to a large percentage of developers
* It allows rapid development
* It's highly readable, allowing intents to be expressed clearly in code

# Contact

If you have any questions regarding the tool set please feel free to contact us and we'll try to
provide you with help or other information.

You can contact us at leakproofing@expressvpn.com.
