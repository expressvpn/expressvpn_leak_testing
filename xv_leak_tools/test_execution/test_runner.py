import copy
import json
import gc
import os

import xv_leak_tools.manual_input

from xv_leak_tools import tools_root, tools_user
from xv_leak_tools.exception import XVEx
from xv_leak_tools.helpers import exception_to_string
from xv_leak_tools.log import L
from xv_leak_tools.path import makedirs_safe
from xv_leak_tools.test_components.component import ComponentNotSupported
from xv_leak_tools.test_device.device_discovery import DeviceDiscovery
from xv_leak_tools.test_framework.assertions import LeakTestFail

STARS = "******************************"

class TestRunStep:

    # pylint: disable=too-few-public-methods

    def __init__(self, up=None, down=None, up_desc=None, down_desc=None):
        self.up = up
        self.down = down
        self.up_desc = up_desc
        self.down_desc = down_desc

class TestRun:

    def __init__(self, test_config):
        self._config = test_config
        self._devices = {}
        self._test_class_instance = None
        self._exceptions = []
        self._output_directory = None
        self._ran = False

    def name(self):
        return self._config['name']

    def config(self):
        return self._config

    def ran(self):
        return self._ran

    def set_ran(self):
        self._ran = True

    def test_class_instance(self):
        return self._test_class_instance

    def set_test_class_instance(self, test_class_instance):
        self._test_class_instance = test_class_instance

    def output_directory(self):
        return self._output_directory

    def set_output_directory(self, output_directory):
        self._output_directory = output_directory

    def devices(self):
        return self._devices

    def set_devices(self, devices):
        self._devices = devices

    def register_exception(self, step, exception):
        # We use a list so that failures are recorded in the order they occur (as opposed to a dict)
        self._exceptions.append((step, exception))

    def passed(self):
        return self.ran() and len(self._exceptions) == 0

    def failed(self):
        return self.ran() and len(self._exceptions) != 0 and \
               isinstance(self._exceptions[0][1], LeakTestFail)

    def errored(self):
        return self.ran() and not self.passed() and not self.failed()

    def exceptions(self):
        return self._exceptions

    def user_interrupt(self):
        for _, ex in self._exceptions:
            if isinstance(ex, KeyboardInterrupt):
                return True
        return False

class TestRunner:

    # pylint: disable=no-self-use

    def __init__(self, context, devices, tests):
        self._context = context
        self._device_discovery = DeviceDiscovery(context, devices)
        self._test_runs = [TestRun(self._check_and_clean_test_config(test)) for test in tests]
        self._test_directory_names = []
        self._component_factory = self._context['component_factory']
        self._test_factory = self._context['test_factory']

    @staticmethod
    def configure_logger(output_directory=None, level=L.INFO, describe=False, report=False):
        trace_logfile = None
        if output_directory:
            trace_logfile = os.path.join(output_directory, 'log.txt')

        describe_logfile = None
        if describe and output_directory:
            describe_logfile = os.path.join(output_directory, 'description.txt')

        report_logfile = None
        if report and output_directory:
            report_logfile = os.path.join(output_directory, 'system_report.txt')

        L.configure({
            'trace': {
                'file_format': '%(asctime)s %(levelname)s: %(message)s',
                'logfile': trace_logfile,
                'level': level,
            },
            'describe': {
                'file_format': '%(message)s',
                'logfile': describe_logfile,
            },
            'report': {
                'stream_format': None,
                'file_format': '%(message)s',
                'logfile': report_logfile,
            },
        })

    def _check_and_clean_test_config(self, test):
        L.debug("Cleaning test config: {}".format(test))
        # Always make a full copy as the test setup will change the config, e.g. by swapping device
        # configs for actual devices
        test = copy.deepcopy(test)

        # Now add missing keys etc so the user can be less verbose when writing test configs
        # Could get smarter about this but right now it's not really worth it. If the config spec
        # grows then consider something better.
        if 'devices' not in test:
            test['devices'] = []
        if 'parameters' not in test:
            test['parameters'] = {}

        # TODO: Consider checking uniqueness of devices. Anything else to verify?
        for device in test['devices']:
            if 'components' not in device:
                device['components'] = {}

            for name, config in list(self._context['default_device_components'].items()):
                if name in device['components']:
                    continue
                device['components'][name] = config

        return test

    def _output_directory_for_test(self, test_name):
        index = 1
        directory_name = "{}_{}".format(test_name, index)
        while directory_name in self._test_directory_names:
            index += 1
            directory_name = "{}_{}".format(test_name, index)
        self._test_directory_names.append(directory_name)
        directory_name = os.path.join(self._context['output_directory'], directory_name)
        return os.path.abspath(directory_name)

    def _build_all_components_for_device(self, device, configs):
        for component_name in self._component_factory.builder_names():
            try:
                device[component_name] = self._component_factory.build(
                    component_name, device, configs.get(component_name, {}))
                if device[component_name] is None:
                    raise XVEx("Component factory returned None for component type {} {}"
                               .format(device, component_name))
            except ComponentNotSupported as ex:
                # It's perfectly fine for building to fail. Some components can't be built on
                # certain devices. However, if any other form of exception occurs then propagate it
                # so we don't mask unexpected issues.
                L.verbose("Can't build component {} for device {}: {}".format(
                    component_name, device.device_id(), ex))

    def _devices_for_test(self, test_config):
        # TODO: Change this doc
        '''Each test specifies a list of devices (via device_id) which it wants to use. This
        function "finds" these devices and creates a dictionary of device objects indexes by
        device_id for the test. Note that we do the discovery every time we run a test, rather than
        caching the devices. This is because tests can request different components for the same
        device and we don't want cross contamination.'''

        devices_for_test = {}
        for test_device in test_config['devices']:
            device = self._device_discovery.discover_device(test_device['discovery_keys'])
            L.debug("Got device {} for test {}".format(device.device_id(), test_config['name']))

            # We try to build every component for every device.
            self._build_all_components_for_device(device, test_device['components'])
            devices_for_test[test_device['device_name']] = device

        return devices_for_test

    # TODO: Slight issue here. If files are pulled in from outside the main folder then pycache
    # can be owned by root. Need to make the test suite smarter there.
    def _ensure_files_not_owned_by_root(self):
        userid = tools_user()[0]
        # Ensure all output files are not owned by root
        os.chown(self._context['output_directory'], userid, -1)
        for root, dirs, files in os.walk(self._context['output_directory']):
            for dir_ in dirs:
                os.chown(os.path.join(root, dir_), userid, -1)
            for file_ in files:
                os.chown(os.path.join(root, file_), userid, -1)

        # Ensure pyc files are not owned by root
        for root, dirs, files in os.walk(tools_root()):
            if '__pycache__' not in root:
                continue
            for file_ in files:
                if os.path.splitext(file_)[1] != ".pyc":
                    continue
                os.chown(os.path.join(root, file_), userid, -1)

    def _prepare_output_directory(self, test_run):
        test_output_directory = self._output_directory_for_test(test_run.name())
        makedirs_safe(test_output_directory)
        # Ensure the test run dir isn't owned by root from the beginning. Otherwise non-root
        # test runs can't access this directory.
        self._ensure_files_not_owned_by_root()
        test_run.set_output_directory(test_output_directory)

    def _prepare_logger(self, test_run):
        TestRunner.configure_logger(
            test_run.output_directory(),
            level=getattr(L, self._context['log_level']),
            describe=True,
            report=True)

    def _restore_logger(self, _):
        TestRunner.configure_logger(self._context['output_directory'])

    def _prepare_devices(self, test_run):
        devices = self._devices_for_test(test_run.config())
        test_run.set_devices(devices)
        for _, device in list(devices.items()):
            device.setup()

    def _release_devices(self, test_run):
        for _, device in list(test_run.devices().items()):
            device.teardown()
        # TODO: Move this into device teardown (above)
        self._device_discovery.release_devices()

    def _prepare_test_class(self, test_run):
        test_class_instance = self._test_factory.create(
            test_run.name(), test_run.devices(), test_run.config()['parameters'])
        test_run.set_test_class_instance(test_class_instance)
        L.describe("Test docs:\n{}".format(test_class_instance.__class__.__doc__))

    def _setup_test(self, test_run):
        test_run.test_class_instance().setup()

    def _report_info(self, test_run):
        test_run.test_class_instance().report_info()

    def _execute_test(self, test_run):
        test_run.test_class_instance().test()

    def _teardown_test(self, test_run):
        test_run.test_class_instance().teardown()

    def run_one(self, test_run):
        L.info("Running test: {}".format(test_run.name()))
        L.debug("Test Config:\n{}".format(json.dumps(test_run.config(), indent=2)))

        test_run.set_ran()

        steps = [
            TestRunStep(up=self._prepare_output_directory, up_desc="Prepare output directory"),
            TestRunStep(
                up=self._prepare_logger,
                up_desc="Prepare logging",
                down=self._restore_logger,
                down_desc="Restore Logging"),
            TestRunStep(
                up=self._prepare_devices,
                up_desc="Prepare devices",
                down=self._release_devices,
                down_desc="Release Devices"),
            TestRunStep(up=self._prepare_test_class, up_desc="Create test class"),
            TestRunStep(
                up=self._setup_test,
                down=self._teardown_test,
                up_desc="Run test setup",
                down_desc="Run test teardown"),
            TestRunStep(up=self._report_info, up_desc="Report info for test"),
            TestRunStep(up=self._execute_test, up_desc="Execute the test"),
        ]

        def exception_string(ex):
            '''KeyboardInterrupt gives no msg so let's make it clear that this is what happened'''
            if isinstance(ex, KeyboardInterrupt):
                return "Keyboard interrupt"
            return str(ex)

        last_step_index = 0
        for last_step_index, step in enumerate(steps):
            if not step.up:
                continue
            try:
                L.info("Executing test step: {}".format(step.up_desc))
                step.up(test_run)
            except BaseException as ex:
                L.error(
                    "Exception occurred during test step '{}'\nEXCEPTION: {}".format(
                        step.up_desc, exception_string(ex)))
                test_run.register_exception(step.up_desc, ex)
                break

        for step_index in reversed(range(0, last_step_index + 1)):
            step = steps[step_index]
            if not step.down:
                continue
            try:
                L.info("Executing test step: {}".format(step.down_desc))
                step.down(test_run)
            except BaseException as ex:
                L.error(
                    "Exception occurred during teardown in test step '{}'\nEXCEPTION: {}".format(
                        step.down_desc, exception_string(ex)))
                test_run.register_exception(step.down_desc, ex)
                # Keep running teardown steps even on failure

        L.debug("Forcing garbage collection to clean up after test run")
        gc.collect()

    def _summarise_run(self, test_runs):
        num_ran = sum(1 for run in test_runs if run.ran())
        passes = [run for run in test_runs if run.passed()]
        failures = [run for run in test_runs if run.failed()]
        errors = [run for run in test_runs if run.errored()]

        L.info("{} Test Run Summary {}".format(STARS, STARS))
        for pass_ in passes:
            L.info("PASSED: {}".format(pass_.name()))
        for fail in failures:
            L.info("FAILED: {}".format(fail.name()))
        for error in errors:
            L.info("ERROR : {}".format(error.name()))

        L.info("Ran {} / {} tests: {} passes, {} fails, {} errors".format(
            num_ran, len(test_runs), len(passes), len(failures), len(errors)))
        return len(failures) + len(errors)

    def run(self):
        if self._context['allow_manual']:
            xv_leak_tools.manual_input.allow_manual_input()

        for itest, test_run in enumerate(self._test_runs):
            try:
                L.info("\n\n {} Test {} / {} {}\n".format(
                    STARS, itest + 1, len(self._test_runs), STARS))

                self.run_one(test_run)

                if test_run.passed():
                    L.info("Test {} passed".format(test_run.name()))
                    continue

                if test_run.user_interrupt():
                    L.error("Abandoning tests due to keyboard interrupt!")
                    break

                exceptions = test_run.exceptions()
                first_exception = exceptions[0]
                # LeakTestFail is different from other exceptions. A LeakTestFail means that the
                # test failed an expectation (assertion). Any other type of exception means
                # something happened we weren't expecting.
                if test_run.failed():
                    L.error("Test {} failed at step '{}' due to assertion:\n{}".format(
                        test_run.name(), first_exception[0],
                        exception_to_string(first_exception[1])))
                else:
                    L.error("Test {} errored at step '{}' due to exception:\n{}".format(
                        test_run.name(), first_exception[0],
                        exception_to_string(first_exception[1])))

                if len(exceptions) > 1:
                    L.warning("Subsequent errors occurred in the test run!")
                    for failure in exceptions[1:]:
                        L.warning("Test step '{}'' errored with:\n{}".format(
                            failure[0], exception_to_string(failure[1])))

                if not self._context['stop_on_fail']:
                    continue

                L.error('Abandoning further tests due to test failure')
                break
            except BaseException as ex:
                L.error(
                    "FATAL ERROR: Unexpected error thrown from test suite. Test run will be "
                    "aborted: {}".format(exception_to_string(ex)))

        num_failures = self._summarise_run(self._test_runs)

        self._device_discovery.cleanup()

        # Do this just in case we ever end up running again without restarting the interpretor
        xv_leak_tools.manual_input.disallow_manual_input()

        # Need to terminate logging in order to close log files and thus chown them to non-root.
        L.terminate()
        self._ensure_files_not_owned_by_root()
        return num_failures
