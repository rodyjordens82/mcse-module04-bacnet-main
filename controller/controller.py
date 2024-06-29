import os
import random

from bacpypes.debugging import bacpypes_debugging, ModuleLogger
from bacpypes.consolelogging import ConfigArgumentParser

from bacpypes.core import run

from bacpypes.primitivedata import Real
from bacpypes.object import AnalogValueObject, Property, register_object_type
from bacpypes.errors import ExecutionError

from bacpypes.app import BIPSimpleApplication
from bacpypes.local.device import LocalDeviceObject

class RandomValueProperty(Property):

    def __init__(self, identifier, value=0.0):
        Property.__init__(self, identifier, Real, default=value, optional=True, mutable=True)
        self.instance_values = {identifier: value}

    def ReadProperty(self, obj, arrayIndex=None):
        if arrayIndex is not None:
            raise ExecutionError(errorClass='property', errorCode='propertyIsNotAnArray')

        return self.instance_values.get(obj.objectIdentifier, 0.0)

    def WriteProperty(self, obj, value, arrayIndex=None, priority=None, direct=False):
        if not self.mutable:
            raise ExecutionError(errorClass='property', errorCode='writeAccessDenied')

        self.instance_values[obj.objectIdentifier] = value

bacpypes_debugging(RandomValueProperty)

class RandomAnalogValueObject(AnalogValueObject):

    properties = [
        RandomValueProperty('presentValue'),
    ]

    def __init__(self, identifier, objectName, value=0.0, **kwargs):
        # Initialize the parent class
        AnalogValueObject.__init__(self, objectIdentifier=identifier, objectName=objectName, **kwargs)

        # Set the presentValue property using the instance property
        self._properties['presentValue'].instance_values[identifier] = value

bacpypes_debugging(RandomAnalogValueObject)
register_object_type(RandomAnalogValueObject)

def main():
    args = ConfigArgumentParser(description=__doc__).parse_args()

    this_device = LocalDeviceObject(
        objectName=args.ini.objectname,
        objectIdentifier=('device', int(args.ini.objectidentifier)),
        maxApduLengthAccepted=int(args.ini.maxapdulengthaccepted),
        segmentationSupported=args.ini.segmentationsupported,
        vendorIdentifier=int(args.ini.vendoridentifier),
    )

    this_application = BIPSimpleApplication(this_device, args.ini.address)

    ravo1 = RandomAnalogValueObject(
        identifier=('analogValue', 1),
        objectName='light',
        value=5.0,
    )
    this_application.add_object(ravo1)

    ravo2 = RandomAnalogValueObject(
        identifier=('analogValue', 2),
        objectName='locking',
        value=1.0,
    )
    this_application.add_object(ravo2)
    
    ravo3 = RandomAnalogValueObject(
        identifier=('analogValue', 3),
        objectName='fire',
        value=1.0,
    )
    this_application.add_object(ravo3)

    ravo4 = RandomAnalogValueObject(
        identifier=('analogValue', 4),
        objectName='camera',
        value=5.0,
    )
    this_application.add_object(ravo4)
    
    run()

if __name__ == '__main__':
    main()
