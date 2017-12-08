from desktop_local_tests.disrupter import Disrupter
from xv_leak_tools.exception import XVEx
from xv_leak_tools.log import L

class MacOSDNSReorderServicesDisrupter(Disrupter):

    def __init__(self, device, parameters):
        super().__init__(device, parameters)
        self._restrict_parameters(must_disrupt=True, must_restore=False)

    def _swap_highest_priority_services(self):
        def active_service_indices(services):
            for service in services:
                if service.active():
                    yield services.index(service)

        services = self._device['network_tool'].network_services_in_priority_order()
        try:
            active_service_index = active_service_indices(services)
            i = next(active_service_index)
            j = next(active_service_index)
            L.debug('Swapping {}, {}'.format(services[i], services[j]))
            services[i], services[j] = services[j], services[i]
        except StopIteration:
            raise XVEx('There must be at least two active services')

        self._device['network_tool'].set_network_service_order(services)

    def disrupt(self):
        L.describe('Swap the two highest-priority active network services')
        self._swap_highest_priority_services()

    def teardown(self):
        self._swap_highest_priority_services()
        super().teardown()
