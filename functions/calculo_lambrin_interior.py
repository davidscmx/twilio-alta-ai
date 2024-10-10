import math

from budget_classes import BudgetCalculator, MaterialBudgetType, custom_format


def calculate_cost_lambrin_interior(area):
    # Creating instances for each item
    tablaroca = MaterialBudgetType(
        material_name='Tablaroca 1/2" Ultralight (pza.)',
        material_cost=172.00,
        quantity_func=lambda area=area: math.ceil(area / 3))

    aislhogar = MaterialBudgetType(
        material_name='AISLHOGAR 2 1/2" x 0.61m x 15.24 m (rollo)',
        material_cost=630.00,
        quantity_func=lambda area=area: math.ceil(area / 9.3))

    poste = MaterialBudgetType(
        material_name='Poste 1 5/8" x 3m Cal. 26 (pza.)',
        material_cost=86.00,
        quantity_func=lambda area=area: math.ceil(area * 1.8 / 3))

    canal = MaterialBudgetType(
        material_name='Canal 1 5/8" x 3m Cal. 26 (pza.)',
        material_cost=71.00,
        quantity_func=lambda area=area: math.ceil(area * 0.8 / 3))

    clavo_pistola = MaterialBudgetType(
        material_name='Clavo p/ Pistola 1" (pza.)',
        material_cost=1.10,
        quantity_func=lambda area=area: math.ceil(
            (2 * math.ceil(area * 1.8 / 3)) / 100) * 100)

    fulminante = MaterialBudgetType(
        material_name='Fulminante Cal. 22 (pza.)',
        material_cost=2.95,
        quantity_func=lambda area=area: math.ceil(
            (2 * math.ceil(area * 1.8 / 3)) / 100) * 100)

    tornillo_fina = MaterialBudgetType(
        material_name='Tornillo 1" Fina (pza.)',
        material_cost=0.20,
        quantity_func=lambda area=area: math.ceil(
            (35 * math.ceil(area / 3)) / 100) * 100)

    tornillo_mini = MaterialBudgetType(
        material_name='Tornillo Mini 1/2" PN (pza.)',
        material_cost=0.20,
        quantity_func=lambda area=area: math.ceil(
            (15 * math.ceil(area / 3)) / 100) * 100)

    redimix_pasta = MaterialBudgetType(
        material_name='Redimix Pasta 22 kg (Caja)',
        material_cost=299.00,
        quantity_func=lambda area=area: math.ceil(area / 20))

    perfacinta = MaterialBudgetType(
        material_name='Perfacinta 75m (Rollo)',
        material_cost=78.00,
        quantity_func=lambda area=area: math.ceil(area * 0.028))

    # List of materials
    materials = [
        tablaroca, aislhogar, poste, canal, clavo_pistola, fulminante,
        tornillo_fina, tornillo_mini, redimix_pasta, perfacinta
    ]

    # Creating BudgetCalculator instance
    budget_calculator = BudgetCalculator(materials)

    # Calculating quantities and total prices
    quantities = {
        material.material_name: material.quantity_of_material
        for material in materials
    }
    total_prices = {
        material.material_name: material.price_per_unit
        for material in materials
    }

    # Returning the budget estimate dictionary
    return {
        "success": "true",
        "area": custom_format(area, n_decim=2),
        "cantidades por articulo": quantities,
        "precio total por artículo": {
            k: custom_format(v)
            for k, v in total_prices.items()
        },
        "subtotal": custom_format(budget_calculator.subtotal),
        "IVA": custom_format(budget_calculator.iva),
        "total_cost": custom_format(budget_calculator.total)
    }
