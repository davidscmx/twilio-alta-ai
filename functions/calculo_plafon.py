import math


def format_number(num, is_int=False):
    """Format a number with commas."""
    if is_int:
        return "{:,}".format(math.ceil(num))
    return "{:,.1f}".format(num)


def calcular_costo_plafon_reticular(length, width, plafon_type):
    # Fetch the area and cost for the given plafon type
    # Default area if plafon_type not found
    plafon_area = plafon_areas.get(plafon_type, 0.3721)
    # Default cost if plafon_type not found
    plafon_cost = plafon_costs.get(plafon_type, 304)

    area = length * width
    quantities = {
        "Ángulo Perimetral Donn x 3.66m (pza.)":
        math.ceil((2 * length + 2 * width) / 3.66),
        "Plafon seleccionado":
        math.ceil(area / plafon_area),
        "Tee Principal Donn x 3.66m (pza.)":
        math.ceil(area * 0.22),
        "Tee Conectora Donn x 1.22m (pza.)":
        math.ceil(area / 0.744),
        "Tee Conectora Donn x 0.61m (pza.)":
        math.ceil(area / 0.744),
        "Alambre Cal.14 (kg.)":
        math.ceil(0.06 * area)
    }

    prices_per_unit = {
        "Ángulo Perimetral Donn x 3.66m (pza.)": 189,
        "Plafon seleccionado": plafon_cost,
        "Tee Principal Donn x 3.66m (pza.)": 335,
        "Tee Conectora Donn x 1.22m (pza.)": 97,
        "Tee Conectora Donn x 0.61m (pza.)": 48,
        "Alambre Cal.14 (kg.)": 53
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

    return {
        "success": "true",
        "area": format_number(area, is_int=False),
        "cantidades por articulo": quantities,
        "precio total por artículo": {
            k: "{:.1f}".format(v)
            for k, v in total_prices.items()
        },
        "subtotal": format_number(subtotal, is_int=False),
        "IVA": format_number(tax, is_int=False),
        "total_cost": format_number(total_cost, is_int=False)
    }


plafon_areas = {
    'Frost 414 0.61m x 0.61m': 0.3721,
    'Glaciar 707 0.61m x 0.61m': 0.3721,
    'Sandrift 808 0.61m x 0.61m': 0.3721,
    'Auratone Fissured 506 0.61m x 0.61m': 0.3721,
    'Radar 2202 0.61m x 0.61m': 0.3721,
    'Olympia 4221 0.61m x 0.61m LS': 0.3721,
    'Eclipse 76775 0.61m x 0.61m': 0.3721,
    'Mars LS 86785 0.61m x 0.61m LS': 0.3721,
    'Millenia 76705 0.61m x 0.61m LS': 0.3721,
    'Radar 2410 0.61m x 1.22m': 0.7442,
    'Auratone Fissured 562 0.61m x 1.22m': 0.7442,
    'Texturizada Astral / SOLAR 3/8" x 0.61m x 1.22m': 0.7442,
    'Clean Room 56091A 0.61m x 1.22m': 0.7442,
    'Placa Tablaroca c/vinil 3270 0.61m x 1.22m': 0.7442,
}

plafon_costs = {
    'Frost 414 0.61m x 0.61m': 304,
    'Glaciar 707 0.61m x 0.61m': 304,
    'Sandrift 808 0.61m x 0.61m': 304,
    'Auratone Fissured 506 0.61m x 0.61m': 128,
    'Radar 2202 0.61m x 0.61m': 139,
    'Olympia 4221 0.61m x 0.61m LS': 199,
    'Eclipse 76775 0.61m x 0.61m': 283,
    'Mars LS 86785 0.61m x 0.61m LS': 376,
    'Millenia 76705 0.61m x 0.61m LS': 283,
    'Radar 2410 0.61m x 1.22m': 230,
    'Auratone Fissured 562 0.61m x 1.22m': 197,
    'Texturizada Astral / SOLAR 3/8" x 0.61m x 1.22m': 89,
    'Clean Room 56091A 0.61m x 1.22m': 590,
    'Placa Tablaroca c/vinil 3270 0.61m x 1.22m': 210,
}
