{
    "name": "calcular_costo_plafon_reticular",
    "description": "Calcula el costo de materiales para un plafón corrido basado en las dimensiones proporcionadas.",
    "parameters": {
        "type": "object",
        "properties": {
            "ancho": {
                "type": "number",
                "description": "El ancho del plafón en metros."
            },
            "largo": {
                "type": "number",
                "description": "El largo del plafón en metros."
            }
        },
        "required": ["ancho", "largo"]
    }
}