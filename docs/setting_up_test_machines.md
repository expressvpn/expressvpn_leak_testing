These docs details how to fully setup a Mac, Linux or Windows machine so that it can run the leak
test tools.

Note that mobile devices currently don't need this setup as they can't run the python test suite.

Test device setup can be simplified by using the provided ansible scripts. See TODO for how to use
ansible for setup. The result of following the steps below or using ansible is the same.

> TODO: ansible not fully supported yet (manual steps only for now)

# A Note on Users

We find it convenient to have a consistent user across all our test devices. The main benefit is
that we always know what the expected user name is for any machine.

We always name the default user `xv_leak_test`. This is the user which the test framework ssh-es
into. The user has passwordless `sudo` in order to simplify privilege escalation for automatic
tests.

> On Windows we assume that we're always running as an administrator. Due to the differences in
  permission models between posix system this is just the simplest approach.

It's not essential that you create such a user but it's recommended that you follow a similar
approach.

* [Linux](setting_up_linux.md)
* [MacOS](setting_up_macos.md)
* [Windows](setting_up_windows.md)
