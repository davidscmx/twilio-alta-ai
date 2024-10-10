import math

from budget_classes import BudgetCalculator, MaterialBudgetType, custom_format


def calculate_cost_lambrin_exterior(area):
    # Creating instances for each item
    foamular = MaterialBudgetType('Foamular 1" 1.22m x 2.44m (pza.)',
                                  462.00,
                                  lambda area=area: math.ceil(area / 3))

    recubrimiento_base_usg = MaterialBudgetType(
        'Recubrimiento Base USG 23kg (pza.)',
        491.00,
        lambda area=area: math.ceil(area / 12))

    recubrimiento_base_crest = MaterialBudgetType(
        'Recubrimiento Base Crest 20kg (pza.)',
        273.00,
        lambda area=area: math.ceil(area / 6))

    malla_fibra_vidrio = MaterialBudgetType(
        'Malla Fibra de Vidrio 50m x 1m (pza.)',
        900.00,
        lambda area=area: math.ceil(area / 50))

    clavo_concreto = MaterialBudgetType('Clavo p/concreto 2" (kg.)',
                                        82.00,
                                        lambda area=area: math.ceil(area / 50))

    materials = [
        foamular,
        recubrimiento_base_usg,
        recubrimiento_base_crest,
        malla_fibra_vidrio,
        clavo_concreto
    ]

    budget_calculator = BudgetCalculator(materials)

    quantities = {
        material.material_name:
        custom_format(material.quantity_of_material, is_int=True)
        for material in materials
    }
    total_prices = {
        material.material_name: custom_format(material.price_per_unit)
        for material in materials
    }

    print({
        "success": "true",
        "area": custom_format(area, n_decim=2),
        "cantidades por articulo": quantities,
        "precio total por artículo": total_prices,
        "subtotal": custom_format(budget_calculator.subtotal),
        "IVA": custom_format(budget_calculator.iva),
        "total_cost": custom_format(budget_calculator.total)
    })
    return {
        "success": "true",
        "area": custom_format(area, n_decim=2),
        "cantidades por articulo": quantities,
        "precio total por artículo": total_prices,
        "subtotal": custom_format(budget_calculator.subtotal),
        "IVA": custom_format(budget_calculator.iva),
        "total_cost": custom_format(budget_calculator.total)
    }
