from product import Product

class Catalog:
    def __init__(self, products=None):
        self.products = products or []

    @staticmethod
    def from_list(data):
        return Catalog([Product.from_dict(p) for p in data])

    def to_list(self):
        return [p.to_dict() for p in self.products]

    def list_all(self):
        return self.products

    def get_by_id(self, product_id):
        for p in self.products:
            if p.id == product_id:
                return p
        return None

    def search(self, keyword):
        keyword = keyword.lower()
        return [
            p for p in self.products
            if keyword in p.title.lower()
        ]

    def filter_by_category(self, category):
        return [
            p for p in self.products
            if p.category.lower() == category.lower()
        ]

    def has_stock(self, product_id, qty):
        product = self.get_by_id(product_id)
        return product and product.stock >= qty

    def reduce_stock(self, product_id, qty):
        product = self.get_by_id(product_id)
        if not product:
            raise ValueError("Product not found")
        if product.stock < qty:
            raise ValueError("Insufficient stock")
        product.stock -= qty
    
    def add_product(self, product):
        if not isinstance(product, Product):
            raise TypeError("product must be a Product instance")

        if self.get_by_id(product.id):
            raise ValueError(f"Product with id {product.id} already exists")

        self.products.append(product)