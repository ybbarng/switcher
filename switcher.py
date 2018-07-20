from time import sleep

from bluepy.btle import Scanner
from bluepy.btle import Peripheral
import bluepy.btle


bluepy.btle.Debugging = False


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

    def __init__(self, share_code, mac_address, callback):
        self.callback = callback
        self.run(share_code)

    def run(self, share_code):
        scan_timeout = 10 # seconds
        scanner = Scanner()
        switcher = None
        retry = True
        while (retry):
            try:
                print('Scanning...')
                devices = scanner.scan(scan_timeout)
                for device in devices:
                    name = None
                    for ad_type, description, value in device.getScanData():
                        if ad_type == 9:
                            name = value
                    if name is None or 'SWITCHER_M' not in name:
                        continue
                    print('A switcher is found: {}({})'.format(name, device.addr))
                    if device.connectable:
                        print('Connectable switcher is found.')
                        switcher = device
                        retry = False
                        break
                    else:
                        print('The switcher is busy')
                if switcher is None:
                    print('Connectable switcher is not found. Retry...')
                    sleep(2)
            except Exception as e:
                print('Error on scanning')
                print(e)
        self.connect(switcher.addr, switcher.addrType, share_code)

    def connect(self, address, address_type, share_code):
        self.share_code = share_code
        retry = True
        while retry:
            try:
                print('Try to connect to the switcher...')
                self.switcher = Peripheral(address, address_type)
                retry = False
            except Exception as e:
                print('Error on connecting')
                print(e)
        print('Switcher is connected')
        if self.callback:
            self.callback.on_connected(self)

    def disconnect(self):
        if self.switcher:
            self.switcher.disconnect()
            print('Switcher is disconnected')

    def to_bytes(self, digits):
        return bytearray(int(ch) for ch in str(digits))

    def show_informations(self):
        self.load_uuids()
        self.get_services(True)
        self.get_characteristics(True)

    def load_uuids(self):
        import json

        with open('uuid.json') as f:
            self.uuids = {v: k for k, v in json.load(f).items()}

    def get_uuid_description(self, uuid):
        try:
            return self.uuids[uuid]
        except:
            return 'Unknown'

    def get_services(self, print_services=False):
        print('get_services')
        services = self.switcher.getServices()
        if print_services:
            for service in services:
                uuid = str(service.uuid)
                print('UUID: {} ({})'.format(uuid, self.get_uuid_description(uuid)))

    def get_characteristics(self, print_characteristics=False):
        print('get_characteristics')
        if self.characteristics is None:
            self.characteristics = self.switcher.getCharacteristics()
        if print_characteristics:
            for ch in self.characteristics:
                uuid = str(ch.uuid)
                print('UUID: {} ({})'.format(uuid, self.get_uuid_description(uuid)))
                print('Properties: {} ({})'.format(ch.properties, ch.propertiesToString()))
                print('Handler: 0x{:02x}'.format(ch.getHandle()))
                print('\n')
        return self.characteristics

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
