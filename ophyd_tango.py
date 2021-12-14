import threading
import time

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


class TangoMotorPosition(TangoAttribute):

    """ Wraps a (Sardana) motor position attribute """

    def set(self, value):
        status = Status()

        def write_and_wait():
            """
            Write position and block until write has taken effect,
            meaning that the attribute quality has gone back to
            "VALID". While the attribute is changing to the new position the
            quality is usually "CHANGING".
            """
            try:
                self._attribute_proxy.write(value)
            except tango.DevFailed as exc:
                status.set_exception(exc)
            while self._attribute_proxy.read().quality != tango.AttrQuality.ATTR_VALID:
                time.sleep(0.1)
            status.set_finished()

        threading.Thread(target=write_and_wait).start()
        return status


type_map = {
    tango.AttrWriteType.READ_WRITE: TangoWritableAttribute,
    tango.AttrWriteType.READ: TangoAttribute,
}


class TangoDevice:
    "Wrap a tango.DeviceProxy in the Bluesky interface."

    READ_FIELDS = []
    CONFIG_FIELDS = []

    def __init__(self, device_proxy: tango.DeviceProxy, *, name):
        self.parent = None
        self.name = name
        self.attributes = []
        for field in self.READ_FIELDS:
            class_ = type_map[device_proxy.get_attribute_config(field).writable]
            obj = class_(
                    tango.AttributeProxy(
                        f"{device_proxy.name()}/{field}",
                    ),
                    parent=self,
                    kind=Kind.normal,
                    name="_".join([self.name, field]),
                )
            self.attributes.append(obj)
            setattr(self, field, obj)
        # TODO CONFIG_FIELDS

    def set(self):
        # TODO Implement this next time.
        ...

    def read(self):
        res = {}
        for attr in self.attributes:
            try:
                res.update(attr.read())
            except Exception:
                continue
        return res

    def read_configuration(self):
        res = {}
        for attr in self.attributes:
            try:
                res.update(attr.read_configuration())
            except Exception:
                continue
        return res

    def describe_configuration(self):
        res = {}
        for attr in self.attributes:
            try:
                res.update(attr.describe_configuration())
            except Exception:
                continue
        return res

    def describe(self):
        res = {}
        for attr in self.attributes:
            try:
                res.update(attr.describe())
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


class TangoMotor(TangoDevice):
    READ_FIELDS = [
        "position",
        "velocity",
    ]


if __name__ == "__main__":
    from bluesky.plans import count
    from bluesky.callbacks.core import LiveTable
    from bluesky import RunEngine
    from bluesky.plans import scan
    from bluesky.callbacks.best_effort import BestEffortCallback

    device_proxy = tango.DeviceProxy("sys/tg_test/1")
    attr_proxy = tango.AttributeProxy("sys/tg_test/1/ampli")

    tango_attr = TangoWritableAttribute(attr_proxy)
    tango_device = TangoThingie(device_proxy, name="thingie")

    motor_proxy = tango.DeviceProxy("motor/motctrl04/1")

    # motor = TangoMotor(motor_proxy, name="motor")
    short_scalar = TangoAttribute(tango.AttributeProxy("sys/tg_test/1/short_scalar"))
    motor1 = TangoMotorPosition(tango.AttributeProxy("motor/motctrl01/1/position"),
                                name="motor1")
    RE = RunEngine()
    bec = BestEffortCallback()
    RE.subscribe(bec)

    RE(scan([short_scalar], motor1, 0, 100, 10))
