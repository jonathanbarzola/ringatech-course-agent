import os
import requests
class Tools:
    
    def __init__(self):
        pass
    
    # Obtener las tasas de cambio del dolar
    # Cuánto vale 100 usd en soles? cuánto está el dolar hoy? 3.40 1 USD = 3.4 PEN por ende 100 usd * 3.4

    def obtener_conversion(self, currency: str, money: float):
        print(f"Llamando herramiento obtener_conversion con {currency}, {money}")

        url = "https://open.er-api.com/v6/latest/USD"

        try:
            response = requests.get(url, timeout=30)
            data = response.json()
            tasa_cambio = data['rates'].get(currency, None)
            return float(tasa_cambio) * money
        
        except Exception as e:
            print(f"ERROR: herramienta obtener_conversion con {currency}, {money}")
            return f"ERROR herramienta obtener_conversion con {currency}, {money}"