import math

from pydantic import BaseModel


class CalculateInput(BaseModel):
    ancho: float
    largo: float
    caras: int


def calcular_costo_muro_interior(width, length, faces):
    # Calculate area
    area = width * length * faces

    # Quantities for each item using ceiling function except for 'Clavo p/ concreto'
    quantities = {
        "Tablaroca Ultralight 1/2\"": math.ceil(area / 3),
        "Poste 2 1/2\"x3m. Cal.26": math.ceil(length / 0.61),
        "Canal de Amarre 2 1/2\"x3m. Cal.26": math.ceil((length * 2) / 3.05),
        "Redimix PASTA": math.ceil(area / 28),
        "Perfacinta": math.ceil(area * 0.02),
        "Tornillo 1\" fina": math.ceil(math.ceil(area / 3) * 0.3) * 100,
        "Tornillo mini 1/2\" PN": math.ceil(area * 0.02) * 100,
        "Clavo p/ concreto 1\"": round(area / 128,
                                       2)  # Rounded to two decimal places
    }

    # Prices per unit for each item (assumed from the provided HTML/JS)
    prices_per_unit = {
        "Tablaroca Ultralight 1/2\"": 172.00,
        "Poste 2 1/2\"x3m. Cal.26": 86.00,
        "Canal de Amarre 2 1/2\"x3m. Cal.26": 61.00,
        "Redimix PASTA": 299.00,
        "Perfacinta": 78.00,
        "Tornillo 1\" fina": 0.20,
        "Tornillo mini 1/2\" PN": 0.20,
        "Clavo p/ concreto 1\"": 82.00
    }

    # Calculate total prices for each item and subtotal using mixed rounding
    total_prices = {}
    subtotal = 0
    for item, quantity in quantities.items():
        total_price = round(quantity * prices_per_unit[item], 2)
        total_prices[item] = total_price
        subtotal += total_price

    # Calculate tax and total cost
    tax = round(subtotal * 0.16, 2)
    total_cost = subtotal + tax

    # Format the results as strings with two decimal places
    formatted_results = {
        "success": "true",
        "quantities": quantities,
        "total_prices_per_unit": {
            k: "{:.1f}".format(v)
            for k, v in total_prices.items()
        },
        "subtotal": "{:.1f}".format(subtotal),
        "tax": "{:.1f}".format(tax),
        "total_cost": "{:.1f}".format(total_cost)
    }

    return formatted_results
