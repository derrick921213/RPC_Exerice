import json
from typing import Self
from xmlrpc.server import SimpleXMLRPCServer
from socketserver import ThreadingMixIn
import threading
from Utils import Parser, Permission
from os import makedirs
import bcrypt
import jwt
import datetime


class ThreadXMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
    pass


def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')


def check_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))


SECRET_KEY = 'GFJ6R4n9yP3@RGkA'


def generate_jwt(payload):
    payload['exp'] = datetime.datetime.now() + datetime.timedelta(hours=1)
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token


def verify_jwt(token):
    try:
        decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return decoded
    except jwt.ExpiredSignatureError:
        return 'Token過期'
    except jwt.InvalidTokenError:
        return 'Token無效'


class Server:
    def __init__(self, args: list[str]):
        (self.data, self.user) = Parser(["data.json", "user.json"]).get_data()
        self.isLogin: list[str] = []
        self.index = 0
        self.lock = threading.Lock()

    def login(self: Self, username: str, password: str) -> bool:
        with self.lock:
            if username not in self.user.keys():
                return 10
            if not check_password(password, self.user[username]["password"]):
                return 2
            if username not in self.isLogin:
                self.isLogin.append(username)
            return True

    def register(self: Self, username: str, password: str, role: Permission) -> bool | int:
        with self.lock:
            if username in self.user.keys():
                return 1
            self.user[username] = {
                "password": hash_password(password),
                "role": role
            }
            print(self.user)
            return True

    def create(self, subject: str, content: str, username: str, date: str) -> bool | int:
        with self.lock:
            if username not in self.isLogin:
                return 5
            if subject in self.data.keys():
                return 3
            self.data[subject] = {
                "content": content,
                "username": username,
                "date": date,
                "reply": {}
            }
            return True

    def subject(self) -> list[str]:
        with self.lock:
            result = list(self.data.keys())
            return result

    def subject_data(self, subject: str, columnName: str) -> str:
        with self.lock:
            if subject not in self.data.keys():
                return 4
            result = self.data[subject][columnName]
            return result

    def subject_all(self) -> str:
        with self.lock:
            result = json.dumps(self.data)
            return result

    def reply(self, subject: str, username: str, content: str, date: str) -> bool | int:
        with self.lock:
            if username not in self.user.keys():
                return 10
            if subject not in self.data.keys():
                return 4
            if username in self.isLogin:
                obj = {
                    "index": self.index,
                    "content": content,
                    "date": date
                }
                if username in self.data[subject]["reply"].keys():
                    self.data[subject]["reply"][username].append(obj)
                else:
                    self.data[subject]["reply"][username] = [obj]
                self.index += 1
            return True

    def discussion(self, subject: str) -> str:
        with self.lock:
            result = self.data[subject]
            return result

    def delete(self, subject: str, username: str) -> bool | int:
        with self.lock:
            if username not in self.isLogin:
                return 5
            if username not in self.user.keys():
                return 10
            if subject not in self.data.keys():
                return 4
            print(self.data[subject]["username"])
            print(username)
            if self.data[subject]["username"] == username or self.user[username]["role"] == Permission.ADMIN.value:
                if len(self.data[subject]["reply"]) > 0 and self.user[username]["role"] != Permission.ADMIN.value:
                    return 11
                del self.data[subject]
                return True
            return 8

    def delete_reply(self, subject: str, username: str, reply_owner: str, content: str, index: int) -> bool | int:
        with self.lock:
            if username not in self.isLogin:
                return 5
            if username not in self.user.keys():
                return 10
            if subject not in self.data.keys():
                return 4
            if reply_owner != username and self.user[username]["role"] != Permission.ADMIN.value:
                return 7
            print(reply_owner)
            print(username)
            print(content)
            print(index)
            condition: bool = self.user[username]["role"] == Permission.ADMIN.value
            print(condition)
            if username in self.data[subject]["reply"].keys() or condition:
                data_owner: str = reply_owner
                if condition and reply_owner == username:
                    data_owner = username
                for i, reply in enumerate(self.data[subject]["reply"][data_owner]):
                    if content != reply["content"]:
                        continue
                    if index == reply["index"]:
                        del self.data[subject]["reply"][data_owner][i]
                        if len(self.data[subject]["reply"][data_owner]) == 0:
                            del self.data[subject]["reply"][data_owner]
                        return True
                return 6
            else:
                return 12

    def show(self, username: str) -> list[dict[str:str]]:
        with self.lock:
            if username not in self.isLogin:
                return 5
            if self.user[username]["role"] != Permission.ADMIN.value:
                return 13
            result = self.user
            return result

    def logout(self, username: str) -> bool:
        with self.lock:
            if username not in self.isLogin:
                return 5
            self.isLogin.remove(username)
            return True


def server(args: list[str]):
    service: Server = Server(args)
    (connect_address, port) = Parser(args).connect_address()
    server = ThreadXMLRPCServer((connect_address, int(port)), allow_none=True)
    server.register_instance(service)
    server.register_introspection_functions()
    print(f"Listening on {connect_address}:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        makedirs("DATA", exist_ok=True)
        with open("DATA/data.json", "w") as f:
            json.dump(service.data, f, indent=4)
        with open("DATA/user.json", "w") as f:
            json.dump(service.user, f, indent=4)
