import re

from audrey import Audrey

class AudreyCallback:
    def on_connected(self, audrey):
        print('Audrey is connected!')
        self.show_commands()
        while True:
            command = input()
            if command == 'dis':
                audrey.disconnect()
                break
            else:
                audrey.send_command(command)

    def show_commands(self):
        print('dis')
        print('ON')
        print('OFF')
        print('NORMAL:COOL:24:LOW')
        print('TOGGLE:POWER:ON')


if __name__ == '__main__':
    audrey = Audrey('64:cf:d9:35:9c:74')
    audrey.connect(AudreyCallback())
