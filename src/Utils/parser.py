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
