class CatalogMixin:
    """

    """

    @property
    def display_name(self):
        return self.title if hasattr(self, 'title') else self.name

    @property
    def display_description(self):
        return self.content if hasattr(self, 'content') else self.description

    @property
    def display_price(self):
        if hasattr(self, 'get_total_price') and callable(self.get_total_price):
            return self.get_total_price()
        else:
            return self.price

    @property
    def display_discount(self):
        return hasattr(self, 'discount') if hasattr(self, 'discount') else None

    def __str__(self):
        return self.display_name[:50] + '...' if len(self.display_name) > 50 else self.display_name
