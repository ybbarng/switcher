import re

from bluepy.btle import Scanner, DefaultDelegate

from switcher import Switcher


class ScanDelegate(DefaultDelegate):
    def __init__(self):
        super().__init__()

    def handleDiscovery(self, device, is_new_device, is_new_data):
        if is_new_device:
            print('New device is discovered: {}'.format(device.addr))
        elif is_new_data:
            print('New data is received from: {}'.format(device.addr))


def run(share_code):
    scan_timeout = 20 # seconds

    scanner = Scanner().withDelegate(ScanDelegate())
    retry = True
    while (retry):
        try:
            devices = scanner.scan(scan_timeout)
            retry = False
        except Exception as e:
            print('Error on scanning')
            print(e)

    for device in devices:
        print('Device {} ({}), RSSI={}dB'.format(device.addr, device.addrType, device.rssi))
        name = None
        for ad_type, description, value in device.getScanData():
            print('{} - {}: {}'.format(ad_type, description, value))
            if ad_type == 9:
                name = value
        print('Connectable: {}'.format(device.connectable))
        if name == 'SWITCHER_M' and device.connectable:
            print('Switcher is found.')
            Switcher(device.addr, device.addrType, share_code)


if __name__ == '__main__':
    retry = True
    share_code_pattern = re.compile('^\d{4}$')
    while(retry):
        share_code = input('Enter hashed share code (4 digits):')
        if share_code_pattern.match(share_code):
            break
    run(share_code)
