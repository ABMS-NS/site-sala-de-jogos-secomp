"""
Model de definição de Admininastror

"""

class Admin:
    def __init__(self, username, senha):
        self.username = username
        self.senha = None

    def __repr__(self):
        return f"Admin(username={self.username})"