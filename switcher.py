from bluepy.btle import Peripheral
from time import sleep

class Switcher:
    switcher = None
    battery_handler = None
    switch_handler = None

    def __init__(self, address, address_type):
        retry = True
        while retry:
            try:
                print('Try to connect to the switcher...')
                self.switcher = Peripheral(address, address_type)
                retry = False
            except Exception as e:
                print('Error on connecting')
                print(e)
        try:
            self.run()
        finally:
            print('disconnect from the switcher')
            self.switcher.disconnect()

    def get_services(self):
        services = self.switcher.getServices()
        print('services')
        for service in services:
            print(service.uuid)

    def get_characteristics(self):
        characteristics = self.switcher.getCharacteristics()
        print('characteristics')
        for ch in characteristics:
            print(ch.uuid)
            print(ch.properties)
            print(ch.propertiesToString())
            print(ch.getHandle())
            print('\n')

    def get_descriptors(self):
        """
        Switcher sends no response for this method
        """
        descriptors = self.switcher.getDescriptors()
        print('descriptors')
        print(descriptors)

    def get_battery_handler(self):
        if not self.battery_handler:
            characteristics = self.switcher.getCharacteristics()
            for ch in characteristics:
                if ch.getHandle() == 14:
                    self.battery_handler = ch
                    return ch
        else:
            return self.battery_handler

    def get_switch_handler(self):
        if not self.switch_handler:
            characteristics = self.switcher.getCharacteristics()
            for ch in characteristics:
                if ch.getHandle() == 17:
                    self.switch_handler = ch
                    return ch
        else:
            return self.switch_handler

    def run(self):
        battery_handler = self.get_battery_handler()
        battery = int.from_bytes(battery_handler.read(), byteorder='big')
        print('Battery Status: {}'.format(battery))

        switch = self.get_switch_handler()
        switch.write(bytes([0]))
        print('Switch 1 ON')
        sleep(2)
        switch.write(bytes([1]))
        print('Switch 1 OFF')
        sleep(2)
        switch.write(bytes([2]))
        print('Switch 2 ON')
        sleep(2)
        switch.write(bytes([3]))
        print('Switch 2 OFF')

