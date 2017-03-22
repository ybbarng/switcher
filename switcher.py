from bluepy.btle import Peripheral
from time import sleep

class Switcher:
    switcher = None
    battery_handler = None
    switch_handler = None
    time_handler = None
    uuids = None

    def __init__(self, address, address_type):
        retry = True
        while retry:
            try:
                print('Try to connect to the switcher...')
                self.switcher = Peripheral(address, address_type)
                print('Switcher is connected')
                retry = False
            except Exception as e:
                print('Error on connecting')
                print(e)
        try:
            # self.retrieve_informations()
            self.run()
        finally:
            print('disconnect from the switcher')
            self.switcher.disconnect()

    def retrieve_informations(self):
        self.load_uuids()
        self.get_services()
        self.get_characteristics()

    def load_uuids(self):
        import json

        with open('uuid.json') as f:
            self.uuids = {v: k for k, v in json.load(f).items()}

    def get_uuid_description(self, uuid):
        try:
            return self.uuids[uuid]
        except:
            return 'Unknown'

    def get_services(self):
        services = self.switcher.getServices()
        print('services')
        for service in services:
            uuid = str(service.uuid)
            print('UUID: {} ({})'.format(uuid, self.get_uuid_description(uuid)))

    def get_characteristics(self):
        characteristics = self.switcher.getCharacteristics()
        print('characteristics')
        for ch in characteristics:
            uuid = str(ch.uuid)
            print('UUID: {} ({})'.format(uuid, self.get_uuid_description(uuid)))
            print('Properties: {} ({})'.format(ch.properties, ch.propertiesToString()))
            print('Handler: 0x{:02x}'.format(ch.getHandle()))
            print('\n')

    def get_descriptors(self):
        """
        Switcher sends no response for this method
        """
        descriptors = self.switcher.getDescriptors()
        print('descriptors')
        print(descriptors)

    def get_handler(self, number_of_handler):
        characteristics = self.switcher.getCharacteristics()
        for ch in characteristics:
            if ch.getHandle() == number_of_handler:
                return ch

    def get_battery_handler(self):
        if not self.battery_handler:
            self.battery_handler = self.get_handler(0xe)
        return self.battery_handler

    def get_switch_handler(self):
        if not self.switch_handler:
            self.switch_handler = self.get_handler(0x11)
        return self.switch_handler

    def get_time_handler(self):
        if not self.time_handler:
            self.time_handler = self.get_handler(0x2b)
        return self.time_handler

    def get_battery(self):
        battery_handler = self.get_battery_handler()
        battery = int.from_bytes(battery_handler.read(), byteorder='big')
        return battery

    def get_day_name(self, day):
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        return days[day]

    def get_time(self):
        time_handler = self.get_time_handler()
        day, hours, minutes = time_handler.read()
        return '{} {:02d}:{:02d}'.format(self.get_day_name(day), hours, minutes)

    def manage_switch(self, switch, on=True):
        """
            switch: 1, 2
            on: True / False
        """
        print('Switch {} {}'.format(switch, 'ON' if on else 'OFF'))
        param = (switch - 1) * 2 + (0 if on else 1)
        switch = self.get_switch_handler()
        switch.write(bytes([param]))

    def run(self):
        print('Battery Status: {}'.format(self.get_battery()))
        print('Time : {}'.format(self.get_time()))
