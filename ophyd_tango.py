class TangoAttribute:
    "Wrap a tango.AttributeProxy in the bluesky interface."
    def __init__(self, attribute_proxy, *, parent=None):
        self._attribute_proxy = attribute_proxy
        self.name = self._attribute_proxy.name()
        self.parent = parent

    def read(self):
        reading = self._attribute_proxy.read()
        return {self.name:
                    {'value': reading.value,
                     'timestamp': reading.time.totime()}}

    def describe(self):
        return {self.name:
                    {'shape': extract_shape(self._attribute_proxy.read()),
                     'dtype': 'number', # jsonschema types
                     'source': '...',
                     'unit': '...'}}

    def read_configuration(self):
        return {}

    def describe_configuration(self):
        return {}


class TangoDevice:
    "Wrap a tango.DeviceProxy in the bluesky interface."
    def __init__(self, device_proxy):
        # Use device_proxy.list_attributes() to build structure at connection
        # time.
        ...

def extract_shape(reading):
    shape = []  # e.g. [10, 15]
    if reading.dim_x:
        shape.append(reading.dim_x)
    if reading.dim_y:
        shape.append(reading.dim_y)
    return shape


import tango
# device_proxy = tango.DeviceProxy('sys/tg_test/1')
attr_proxy = tango.AttributeProxy('sys/tg_test/1/double_scalar')
tango_attr = TangoAttribute(attr_proxy)
from bluesky import RunEngine
RE = RunEngine()
from bluesky.plans import count
from bluesky.callbacks.core import LiveTable
