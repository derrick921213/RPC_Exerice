# import signal
from typing import Self
from Server import server
from Client import client

class Main:
    def __init__(self: Self, args: list[str]):
        if len(args) < 2:
            self.help()
            sys.exit(1)
        match args[1]:
            case 'server':
                self.service = server
            case 'client':
                self.service = client
            case _:
                self.help()
                sys.exit(1)
        self.args = args[2:]
        self.service(self.args)

    def help(self):
        print(
            '''Usage: python3 main.py [server|client] [args]\n\n使用json格式的參數: {"host":"","port":""}\n''')

if __name__ == "__main__":
    import sys
    Main(sys.argv)
