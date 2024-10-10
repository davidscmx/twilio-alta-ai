class MaterialBudgetType:

    def __init__(self, material_name, material_cost, quantity_func):
        self.material_name = material_name
        self.material_cost = material_cost
        self.quantity_func = quantity_func

    @property
    def quantity_of_material(self):
        return self.quantity_func()

    @property
    def price_per_unit(self):
        return self.quantity_of_material * self.material_cost


class BudgetCalculator:

    def __init__(self, materials):
        self.materials = materials

    @property
    def subtotal(self):
        return sum(material.price_per_unit for material in self.materials)

    @property
    def iva(self):
        return self.subtotal * 0.16

    @property
    def total(self):
        return self.subtotal + self.iva


# Formatting numbers
def custom_format(num, is_int=False, n_decim=1):
    if is_int:
        result = "{:,.0f}".format(num)
        return result
    result = "{:,.{}f}".format(num, n_decim)
    return result
