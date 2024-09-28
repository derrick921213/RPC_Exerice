import webview
import os
import datetime
import xmlrpc.client
from enum import Enum
import json
import threading
# import signal
from Utils.role import Permission
from Utils.parser import Parser
from Utils.error import Error


class Column(Enum):
    USERNAME = "username"
    DATE = "date"
    CONTENT = "content"
    REPLY = "reply"


class Client:
    TITLE = "UI"
    RETRY_INTERVAL = 5
    MAX_RETRIES = 5

    def __init__(self, args: list[str]):
        self.args = args
        self.server = None
        self.login_user = ""
        self.retry_count = 0
        (self.connect_address, self.port, self.ui) = Parser(
            self.args).connect_address()
        self.connect_to_server()

    def reload_html(self):
        if self.window:
            current_dir = os.path.dirname(os.path.abspath(__file__))
            index_path = os.path.join(current_dir, 'dist', 'index.html')
            self.window.load_html(f'{index_path}')

    def get_retry_status(self) -> str:
        if self.retry_count > 0:
            if self.retry_count <= self.MAX_RETRIES:
                return f"Retrying to connect in {self.RETRY_INTERVAL} seconds... (Attempt {self.retry_count}/{self.MAX_RETRIES})"
            else:
                return f"Max retries ({self.MAX_RETRIES}) reached. Giving up."
        return "Connected"

    def reset_retry(self):
        """Reset the retry count and restart the connection process."""
        self.retry_count = 0
        self.connect_to_server()

    def connect_to_server(self):
        """嘗試連接到伺服器，並設置自動重試機制"""
        connect_address, port = self.connect_address, self.port
        try:
            print(f"Connecting to server at {connect_address}:{port}...")
            self.server = xmlrpc.client.ServerProxy(
                f'http://{connect_address}:{port}')
            self.server.system.listMethods()
            print("Connected to server successfully!")
            self.retry_count = 0
        except Exception as e:
            self.server = None
            print(f"Failed to connect to server: {e}")
            self.retry_count += 1
            if self.retry_count <= self.MAX_RETRIES:
                print(f"Retrying to connect in {self.RETRY_INTERVAL} seconds... (Attempt {
                      self.retry_count}/{self.MAX_RETRIES})")
                threading.Timer(self.RETRY_INTERVAL,
                                self.connect_to_server).start()
            else:
                print(f"Max retries ({self.MAX_RETRIES}) reached. Giving up.")

    def ping(self) -> bool:
        if not self.server:
            return False
        return True

    def register(self, username: str, password: str, role: Permission | str) -> bool | str:
        if isinstance(role, Permission):
            role = role.value
        try:
            ret = self.server.register(username, password, role)
            if not isinstance(ret, bool):
                error = Error(ret)
                return error.message
            else:
                return True
        except Exception as e:
            return f"Connection error: {e}"

    def show(self):
        print(self.server.show())

    def create(self, subject: str, content: str, username: str) -> bool | str:
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            ret = self.server.create(subject, content, username, date)
            if not isinstance(ret, bool):
                error = Error(ret)
                return error.message
            return True
        except Exception as e:
            return f"Connection error: {e}"

    def subject(self) -> list[str]:
        try:
            ret: list[str] = self.server.subject()
            return ret
        except Exception as e:
            return f"Connection error: {e}"

    def subject_data(self, subject: str, columnName: Column) -> bool | str:
        try:
            ret = self.server.subject_data(subject, columnName.value)
            if not isinstance(ret, bool):
                error = Error(ret)
                return error.message
            return True
        except Exception as e:
            return f"Connection error: {e}"

    def login(self, username: str, password: str):
        try:
            ret = self.server.login(username, password)
            if not isinstance(ret, bool):
                error = Error(ret)
                return error.message
            else:
                self.login_user = username
                return True
        except Exception as e:
            return f"Connection error: {e}"

    def reply(self, subject: str, username: str, content: str) -> bool | str:
        date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            ret = self.server.reply(subject, username, content, date)
            if not isinstance(ret, bool):
                error = Error(ret)
                return error.message
            return True
        except Exception as e:
            return f"Connection error: {e}"

    def discussion(self, subject: str) -> str:
        try:
            ret = self.server.discussion(subject)
            data = json.dumps(ret, indent=4)
            return data
        except Exception as e:
            return f"Connection error: {e}"

    def delete(self, subject: str, username: str) -> bool | str:
        try:
            ret = self.server.delete(subject, username)
            if not isinstance(ret, bool):
                error = Error(ret)
                return error.message
            return True
        except Exception as e:
            return f"Connection error: {e}"

    def delete_reply(self, subject: str, username: str, reply_owner: str, content: str, index: int) -> bool | str:
        try:
            ret = self.server.delete_reply(
                subject, username, reply_owner, content, index)
            if not isinstance(ret, bool):
                error = Error(ret)
                return error.message
            return True
        except Exception as e:
            return f"Connection error: {e}"

    def say_hello(self, name: str) -> str:
        return f'Hello {name}'

    def is_login(self) -> bool:
        return bool(self.login_user)

    def get_login_user(self) -> str:
        return self.login_user

    def subject_all(self) -> str:
        try:
            ret = self.server.subject_all()
            return ret
        except Exception as e:
            return f"Connection error: {e}"

    def logout(self) -> bool:
        try:
            ret = self.server.logout(self.login_user)
        except Exception as e:
            pass
        finally:
            self.login_user = ""
        return ret


def adjust_window_size(window):
    js_code = """
    function getContentSize() {
        var body = document.body;
        var html = document.documentElement;
    
        var width = Math.max(body.scrollWidth, body.offsetWidth, html.clientWidth, html.scrollWidth, html.offsetWidth);
        var height = Math.max(body.scrollHeight, body.offsetHeight, html.clientHeight, html.scrollHeight, html.offsetHeight);
    
        return { width: width, height: height };
    }
    getContentSize();
    """
    size = window.evaluate_js(js_code)

    if size:
        width = size['width']
        height = size['height']
        window.resize(width, height)


def on_loaded(window):
    adjust_window_size(window)


# def signal_handler():
#     print("\nExiting...")
#     exit(0)


# signal.signal(signal.SIGINT, signal_handler)


def client(args: list[str]):
    api = Client(args)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    index_path = os.path.join(current_dir, api.ui, 'index.html')
    window = webview.create_window(
        Client.TITLE, index_path, js_api=api, fullscreen=True)
    webview.start(on_loaded, window)
