import threading

from ophyd import Kind
from ophyd.status import Status
import tango


class TangoAttribute:
    "Wrap a tango.AttributeProxy in the bluesky interface."

    def __init__(
        self,
        attribute_proxy: tango.AttributeProxy,
        *,
        parent=None,
        kind=Kind.normal,
        name=None,
    ):
        self._attribute_proxy = attribute_proxy
        if name is None:
            name = self._attribute_proxy.name()
        self.name = name
        self.parent = parent

    @property
    def proxy(self):
        return self._attribute_proxy

    def read(self):
        reading = self._attribute_proxy.read()
        return {self.name: {"value": reading.value, "timestamp": reading.time.totime()}}

    def describe(self):
        return {
            self.name: {
                "shape": extract_shape(self._attribute_proxy.read()),
                "dtype": "number",  # jsonschema types
                "source": self._attribute_proxy.name(),
                "unit": self._attribute_proxy.get_config().unit,
            }
        }

    def read_configuration(self):
        return {}

    def describe_configuration(self):
        return {}


class TangoWritableAttribute(TangoAttribute):
    def set(self, value):
        status = Status()

        def write_and_wait():
            # This blocks until the write is accepted, which in this case means
            # the write is complete. Do not use this approach for a motor or
            # something that takes time to execute the write.
            try:
                self._attribute_proxy.write(value)
            except Exception as exc:
                status.set_exception(exc)
            else:
                status.set_finished()

        threading.Thread(target=write_and_wait).start()
        return status


class TangoDevice:
    "Wrap a tango.DeviceProxy in the Bluesky interface."

    READ_FIELDS = []
    CONFIG_FIELDS = []

    def __init__(self, device_proxy: tango.DeviceProxy, *, name):
        self.name = name
        self.attributes = []
        for field in self.READ_FIELDS:
            self.attributes.append(
                TangoAttribute(
                    tango.AttributeProxy(
                        f"{device_proxy.name()}/{field}",
                    ),
                    parent=self,
                    kind=Kind.normal,
                    name="_".join([self.name, field]),
                )
            )
        # TODO CONFIG_FIELDS

    def read(self):
        res = {}
        for attr in self.attributes:
            try:
                res.update(attr.read())
            except Exception:
                continue
        return res


class TangoThingie(TangoDevice):
    READ_FIELDS = [
        "string_scalar",
        "uchar_scalar",
        "ulong64_scalar",
        "ushort_scalar",
        "ulong_scalar",
    ]


def extract_shape(reading):
    shape = []  # e.g. [10, 15]
    if reading.dim_x:
        shape.append(reading.dim_x)
    if reading.dim_y:
        shape.append(reading.dim_y)
    return shape


device_proxy = tango.DeviceProxy("sys/tg_test/1")
attr_proxy = tango.AttributeProxy("sys/tg_test/1/ampli")

tango_attr = TangoWritableAttribute(attr_proxy)
tango_device = TangoThingie(device_proxy, name="thingie")

from bluesky import RunEngine

RE = RunEngine()
from bluesky.plans import count
from bluesky.callbacks.core import LiveTable
