import math


def calculate_plafon_corrido(ancho, largo):
    # Calculate area
    area = round(ancho * largo, 2)

    # Quantities for each item using ceiling function except for 'Clavo para concreto'
    quantities = {
        "Ángulo de amarre 3m Cal. 26":
        math.ceil(2 * (ancho + largo) / 3),
        "Canaleta de carga 1 1/2\" x 3m Cal. 22":
        math.ceil(ancho * largo * 0.28),
        "Redimix pasta Tablaroca 21.8 kg":
        math.ceil(area / 28),
        "Perfacinta (USA) 75m":
        math.ceil(area * 0.02),
        "Canal Liston 7/8\" x 3m Cal. 26":
        math.ceil(math.floor(largo / 0.61) * ancho / 3),
        "Tablaroca Ultralight 1/2\"":
        math.ceil(area / 3),
        "Tornillo 1\" fina":
        math.ceil(30 * math.ceil(area / 3) / 100) * 100,
        "Tornillo Mini 1/2\" PN":
        math.ceil(area / 3 * 10),
        "Alambre Cal. 18":
        math.ceil(area / 50),
        "Alambre Cal. 14":
        math.ceil(area / 33),
        "Clavo para concreto 1\"":
        round(area / 127, 2),
        "Clavo con ancla 1\"":
        math.ceil(area * 0.7)
    }

    # Prices per unit for each item (assumed from the provided HTML/JS)
    prices_per_unit = {
        "Ángulo de amarre 3m Cal. 26": 34.00,
        "Canaleta de carga 1 1/2\" x 3m Cal. 22": 79.00,
        "Redimix pasta Tablaroca 21.8 kg": 299.00,
        "Perfacinta (USA) 75m": 78.00,
        "Canal Liston 7/8\" x 3m Cal. 26": 45.00,
        "Tablaroca Ultralight 1/2\"": 172.00,
        "Tornillo 1\" fina": 0.20,
        "Tornillo Mini 1/2\" PN": 0.20,
        "Alambre Cal. 18": 58.00,
        "Alambre Cal. 14": 58.00,
        "Clavo para concreto 1\"": 82.00,
        "Clavo con ancla 1\"": 4.50
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
    total_cost = round(subtotal + tax, 2)

    # Format the results as strings with two decimal places
    formatted_results = {
        "success": "true",
        "area": "{:.1f}".format(area),
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
