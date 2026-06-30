import requests


def obtener_conversion(currency: str):
    print(f"Llamando herramiento obtener_conversion con {currency}")

    url = "https://open.er-api.com/v6/latest/USD"

    response = requests.get(url, timeout=30)
    data = response.json()
    tasa_cambio = data['rates'].get(currency, None)
    print(tasa_cambio)


obtener_conversion("PEN")
