import re

from switcher import Switcher

class SwitcherCallback:
    def on_connected(self, switcher):
        print('on_connected')
        print('Battery Status: {}'.format(switcher.get_battery()))
        #print('Shared Hash Code : {}'.format(self.compare_hashed_share_code()))
        print('Authority : {}'.format(switcher.get_authority()))
        print('Time : {}'.format(switcher.get_time()))
        self.show_commands()
        while True:
            params = input().split()
            if params[0] == 'SWITCH':
                # "SWITCH 1 1"
                # "SWITCH 1 0"
                switcher.manage_switch(int(params[1]), parans[2]=='1')
            elif params[0] == 'BAT':
                print('Battery Status: {}'.format(switcher.get_battery()))
            elif params[0] == 'TIME':
                print('Time : {}'.format(switcher.get_time()))
            elif params[0] == 'INFO':
                switcher.show_informations()
            elif params[0] == 'DIS':
                switcher.disconnect()

    def show_commands(self):
        print('SWITCH 1 1')
        print('BAT')
        print('TIME')
        print('INFO')
        print('DIS')


if __name__ == '__main__':
    retry = True
    share_code_pattern = re.compile('^\d{4}$')
    while(retry):
        share_code = input('Enter hashed share code (4 digits):')
        if share_code_pattern.match(share_code):
            break
    switcher = Switcher(share_code, 'df:d2:38:54:db:09', SwitcherCallback())
