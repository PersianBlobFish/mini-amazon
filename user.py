class User:
    def __init__(self, username: str, password_hash: str, cart=None):
        self.username = username
        self.password_hash = password_hash
        self.cart = cart or []

    def to_dict(self) -> dict:
        return {
            "username": self.username,
            "password": self.password_hash,
            "cart": self.cart
        }

    @staticmethod
    def from_dict(d: dict) -> "User":
        return User(
            username=d["username"],
            password_hash=d["password"],
            cart=d.get("cart", [])
        )
