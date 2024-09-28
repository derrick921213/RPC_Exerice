import json
import xmlrpc.client
import datetime
# from Utils import Parser, Error, Permission
from enum import Enum
import getpass


class Permission(Enum):
    ADMIN = "admin"
    USER = "user"


class Parser:
    def __init__(self, args: list[str]):
        self.args = args

    def connect_address(self):
        host: str = 'localhost'
        port: str = "50051"
        if len(self.args) == 1:
            import json
            data: dict[str, str] = json.loads(self.args[0])
            if 'host' in data:
                host = data['host']
            if 'port' in data:
                port = data['port']
        return (host, port)

    def get_data(self) -> tuple[dict, dict]:
        DATA = "DATA"
        from os.path import join, exists
        import json
        user_data = join(DATA, 'user.json')
        server_data = join(DATA, 'data.json')
        if not exists(user_data):
            user_data = {}
        if not exists(server_data):
            server_data = {}
        if user_data:
            with open(user_data, 'r') as f:
                user_data = json.load(f)
        if server_data:
            with open(server_data, 'r') as f:
                server_data = json.load(f)
        return (server_data, user_data)


class Error:
    def __init__(self, error_code: int):
        match error_code:
            case 1:
                message = "Username already exists"
            case 2:
                message = "Username or password is incorrect"
            case 3:
                message = "Subject already exists"
            case 4:
                message = "Subject does not exist"
            case 5:
                message = "User is not logged in"
            case 6:
                message = "Reply does not exist"
            case 7:
                message = "Reply does not belong to user"
            case 8:
                message = "User is not authorized to delete"
            case 9:
                message = "User is not authorized to delete reply"
            case 10:
                message = "User Not Registered"
            case 11:
                message = "Subject has more than 0 replies, cannot delete"
            case 12:
                message = "User has not replied to this subject"
            case 13:
                message = "User is not authorized to view, only Admin can view"
            case _:
                message = f'{error_code}'
        self.message = message

    def __str__(self):
        return self.message


class Column(Enum):
    USERNAME = "username"
    DATE = "date"
    CONTENT = "content"
    REPLY = "reply"


class Client:
    def __init__(self, args: list[str]):
        (connect_address, port) = Parser(args).connect_address()
        self.server = xmlrpc.client.ServerProxy(
            'http://' + connect_address + ':' + str(port))
        self.args = args

    def register(self, username: str, password: str, role: Permission):
        ret = self.server.register(username, password, role.value)
        if not isinstance(ret, bool):
            print(Error(ret))

    def show(self):
        print(self.server.show())

    def create(self, subject: str, content: str, username: str):
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ret = self.server.create(subject, content, username, date)
        if not isinstance(ret, bool):
            print(Error(ret))

    def subject(self):
        print(self.server.subject())

    def subject_data(self, subject: str, columnName: Column):
        ret = self.server.subject_data(subject, columnName.value)
        if not isinstance(ret, bool):
            print(Error(ret))

    def login(self, username: str, password: str):
        ret = self.server.login(username, password)
        if not isinstance(ret, bool):
            print(Error(ret))
        else:
            print("Login success")

    def reply(self, subject: str, username: str, content: str):
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ret = self.server.reply(subject, username, content, date)
        if not isinstance(ret, bool):
            print(Error(ret))

    def discussion(self, subject: str):
        ret = self.server.discussion(subject)
        print(json.dumps(ret, indent=4))

    def delete(self, subject: str, username: str):
        ret = self.server.delete(subject, username)
        if not isinstance(ret, bool):
            print(Error(ret))

    def delete_reply(self, subject: str, username: str, content: str, index: int):
        ret = self.server.delete_reply(subject, username, content, index)
        if not isinstance(ret, bool):
            print(Error(ret))


def client(args: list[str]):
    client = Client(args)

    try:
        while True:
            print("\nOptions:")
            print("1. Register")
            print("2. Login")
            print("3. Create Discussion")
            print("4. Reply to Discussion")
            print("5. View Subject Data")
            print("6. View Discussion")
            print("7. Delete Discussion")
            print("8. Delete Reply")
            print("9. Quit")
            choice = input("\nEnter your choice (1-9): ")

            if choice == "1":
                username = input("Enter username: ")
                password = getpass.getpass("Enter password: ")
                role = input("Enter role (USER/ADMIN): ")
                role_enum = Permission.USER if role.upper() == "USER" else Permission.ADMIN
                client.register(username, password, role_enum)

            elif choice == "2":
                username = input("Enter username: ")
                password = getpass.getpass("Enter password: ")
                client.login(username, password)

            elif choice == "3":
                subject = input("Enter subject: ")
                content = input("Enter content: ")
                username = input("Enter your username: ")
                client.create(subject, content, username)

            elif choice == "4":
                subject = input("Enter subject: ")
                username = input("Enter your username: ")
                content = input("Enter reply content: ")
                client.reply(subject, username, content)

            elif choice == "5":
                subject = input("Enter subject: ")
                column = input("Enter column (USERNAME/DATE/CONTENT/REPLY): ")
                column_enum = Column[column.upper()]
                client.subject_data(subject, column_enum)

            elif choice == "6":
                subject = input("Enter subject: ")
                client.discussion(subject)

            elif choice == "7":
                subject = input("Enter subject: ")
                username = input("Enter your username: ")
                client.delete(subject, username)

            elif choice == "8":
                subject = input("Enter subject: ")
                username = input("Enter your username: ")
                content = input("Enter reply content: ")
                index = int(input("Enter index of the reply to delete: "))
                client.delete_reply(subject, username, content, index)

            elif choice == "9":
                print("Goodbye!")
                break

            else:
                print("Invalid choice, please try again.")
    except KeyboardInterrupt:
        print("\nGoodbye!")


client('{"host":"localhost","port":"50051"}')

# def client(args: list[str]):
#     client = Client(args)
#     client.register("test", "test", Permission.USER)
#     client.register("gg", "gg", Permission.USER)
#     client.register("derrick", "test", Permission.ADMIN)

#     client.login("test", "test")
#     client.login("derrick", "test")
#     client.login("gg", "gg")

#     client.create("test", "test", "test")
#     client.create("tezt", "dikdkdk", "test")
#     client.create("1223", "dikdkdk", "test")
#     client.subject_data("test", Column.USERNAME)

#     client.reply("test", "derrick", "GHHAH")
#     client.reply("test", "derrick", "UURIR")
#     client.reply("test", "gg", "1234")
#     client.reply("test", "gg", "KKEOEO")

#     client.delete_reply("test", "derrick", "GG", 1)
#     client.delete_reply("test", "derrick", "GG", 0)
#     client.delete("test", "test")
#     client.discussion("test")
