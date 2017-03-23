from time import sleep

from bluepy.btle import Peripheral

class Switcher:
    switcher = None
    characteristics = None
    battery_handler = None
    hashed_share_code_handler = None
    authority_handler = None
    time_handler = None
    switch_handler = None
    uuids = None
    share_code = None

    def __init__(self, address, address_type, share_code):
        self.share_code = share_code
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

    def to_bytes(self, digits):
        return bytearray(int(ch) for ch in str(digits))

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
        if self.characteristics is None:
            self.characteristics = self.switcher.getCharacteristics()
        return self.characteristics
        '''
        print('characteristics')
        for ch in characteristics:
            uuid = str(ch.uuid)
            print('UUID: {} ({})'.format(uuid, self.get_uuid_description(uuid)))
            print('Properties: {} ({})'.format(ch.properties, ch.propertiesToString()))
            print('Handler: 0x{:02x}'.format(ch.getHandle()))
            print('\n')
        '''

    def get_descriptors(self):
        """
        Switcher sends no response for this method
        """
        descriptors = self.switcher.getDescriptors()
        print('descriptors')
        print(descriptors)

    def get_handler(self, number_of_handler):
        characteristics = self.get_characteristics()
        for ch in characteristics:
            if ch.getHandle() == number_of_handler:
                return ch
        print('There is no handler: {}'.format(number_of_handler))
        return None

    def get_battery_handler(self):
        if not self.battery_handler:
            self.battery_handler = self.get_handler(0xe)
        return self.battery_handler

    def get_hashed_share_code_handler(self):
        if not self.hashed_share_code_handler:
            self.hashed_share_code_handler = self.get_handler(0x1d)
        return self.hashed_share_code_handler

    def get_authority_handler(self):
        if not self.authority_handler:
            self.authority_handler = self.get_handler(0x1f)
        return self.authority_handler

    def get_time_handler(self):
        if not self.time_handler:
            self.time_handler = self.get_handler(0x2b)
        return self.time_handler

    def get_switch_handler(self):
        if not self.switch_handler:
            self.switch_handler = self.get_handler(0x11)
        return self.switch_handler

    def get_battery(self):
        battery_handler = self.get_battery_handler()
        battery = int.from_bytes(battery_handler.read(), byteorder='big')
        return battery

    def compare_hashed_share_code(self):
        hashed_share_code_handler = self.get_hashed_share_code_handler()
        hashed_share_code = self.to_bytes('0' + self.share_code)
        print('Write: {}'.format(hashed_share_code))
        return hashed_share_code_handler.write(hashed_share_code, True)

    def get_authority(self):
        authority_handler = self.get_authority_handler()
        return authority_handler.read()[0]

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
        if switch not in [1, 2]:
            print('Switch must be 1 or 2')
            return
        print('Switch {} {}'.format(switch, 'ON' if on else 'OFF'))
        param = (switch - 1) * 2 + (0 if on else 1)
        switch = self.get_switch_handler()
        switch.write(bytes([param]))

    def run(self):
        print('Battery Status: {}'.format(self.get_battery()))
        #print('Shared Hash Code : {}'.format(self.compare_hashed_share_code()))
        print('Authority : {}'.format(self.get_authority()))
        print('Time : {}'.format(self.get_time()))
        while True:
            switch, status = input().split()
            self.manage_switch(int(switch), status=='1')
