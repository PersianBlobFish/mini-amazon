class User:
    def __init__(self, username: str, cart=None):
        self.username = username
        self.cart = cart or []

    def to_dict(self) -> dict:
        return {
            "username": self.username,
            "cart": self.cart
        }

    @staticmethod
    def from_dict(d: dict) -> "User":
        return User(
            username=d["username"],
            cart=d.get("cart", [])
        )
