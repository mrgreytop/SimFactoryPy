
class Item():
    def __init__(self, name, stack_cap):
        self.name = name
        self.stack_cap = stack_cap

    def __repr__(self):
        return f"Item({self.name}, {self.stack_cap})"

    def __str__(self):
        return self.name