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
    scan_timeout = 10 # seconds

    scanner = Scanner().withDelegate(ScanDelegate())
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
                if name is None or 'SWITCHER' not in name:
                    continue
                print('Device {} ({}), RSSI={}dB'.format(device.addr, device.addrType, device.rssi))
                print('Connectable: {}'.format(device.connectable))
                if name == 'SWITCHER_M' and device.connectable:
                    print('Connectable switcher is found.')
                    switcher = device
                    retry = False
                    break
            print('Switcher is not found')
        except Exception as e:
            print('Error on scanning')
            print(e)
    Switcher(device.addr, device.addrType, share_code)


if __name__ == '__main__':
    retry = True
    share_code_pattern = re.compile('^\d{4}$')
    while(retry):
        share_code = input('Enter hashed share code (4 digits):')
        if share_code_pattern.match(share_code):
            break
    run(share_code)
