from xv_leak_tools.log import L
from xv_leak_tools.test_framework.assertions import Assertions

class Disrupter(Assertions):

    def __init__(self, device, parameters):
        self._device = device
        self._parameters = parameters
        self._do_disrupt = parameters.get('do_disrupt', True)
        self._do_restore = parameters.get('do_restore', False)
        self.wait_time_for_disruption = parameters.get('wait_time_for_disruption', 0)

    def __str__(self):
        return "{}(do_disrupt={}, do_restore={}, wait_time_for_disruption={}s)".format(
            self.__class__.__name__, self._do_disrupt, self._do_restore,
            self.wait_time_for_disruption)

    @staticmethod
    def _bool_to_not_string(the_bool):
        return "" if the_bool else " not"

    def _restrict_parameters(self, must_disrupt=None, must_restore=None, must_wait=None):
        # This is rather clunky but does the job. Some disrupters just don't make sense to configure
        # one way or the other. So we allow derived classes to enforce this with a single method
        # call.
        if must_disrupt is not None:
            if self._do_disrupt != must_disrupt:
                L.warning(
                    "Disrupter {} can{} do disrupt step. Defaulting to do_disrupt={}".format(
                        self.__class__.__name__, Disrupter._bool_to_not_string(must_disrupt),
                        must_disrupt))
                self._do_disrupt = must_disrupt

        if must_restore is not None:
            if self._do_restore != must_restore:
                L.warning(
                    "Disrupter {} can{} do restore step. Defaulting to do_restore={}".format(
                        self.__class__.__name__, Disrupter._bool_to_not_string(must_restore),
                        must_restore))
                self._do_restore = must_restore

        if must_wait is not None:
            if must_wait and not self.wait_time_for_disruption:
                L.warning(
                    "Disrupter {} must wait for disruption. Defaulting to "
                    "wait_time_for_disruption=65".format(self.__class__.__name__))
                self.wait_time_for_disruption = 65
            elif not must_wait and self.wait_time_for_disruption:
                L.warning(
                    "Disrupter {} must not wait for disruption. Disabling wait for "
                    "disruption".format(self.__class__.__name__))
                self.wait_time_for_disruption = 0

    def setup(self):
        pass

    def teardown(self):
        pass

    def create_disruption(self):
        if self._do_disrupt:
            self.disrupt()

        if self.wait_time_for_disruption:
            L.describe("Wait for VPN application to notice disruption (timeout={})".format(
                self.wait_time_for_disruption))

            self._device['vpn_application'].wait_for_connection_interrupt_detection(
                timeout=self.wait_time_for_disruption)

        if self._do_restore:
            self.restore()

    def disrupt(self):
        L.warning("There's no disrupt action for {}. Did you mean to specify no_disrupt?".format(
            self.__class__.__name__))

    def restore(self):
        L.warning("There's no disrupt action for {}. Did you mean to specify no_restore?".format(
            self.__class__.__name__))
