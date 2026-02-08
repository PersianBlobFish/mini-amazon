class Product:
    def __init__(self, id, title, price, stock, category="general"):
        self.id = id
        self.title = title
        self.price = price
        self.stock = stock
        self.category = category

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "price": self.price,
            "stock": self.stock,
            "category": self.category
        }

    @staticmethod
    def from_dict(d):
        return Product(
            id=d["id"],
            title=d["title"],
            price=d["price"],
            stock=d.get("stock", 0),
            category=d.get("category", "general")
        )
