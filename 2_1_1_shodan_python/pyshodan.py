import os
from dotenv import load_dotenv
from shodansearch import ShodanSearch

def main():
    """
    Función principal que carga la configuración del entorno, inicializa una búsqueda en Shodan
    y muestra los resultados de la búsqueda.
    """
    # Carga variables de entorno desde un archivo .env
    load_dotenv()

    # Obtiene la clave API de Shodan del entorno
    shodan_api_key = os.getenv("SHODAN_API_KEY")

    # Verifica si la clave API está disponible
    if not shodan_api_key:
        raise ValueError("La clave API de SHODAN no está definida en las variables de entorno.")
    try:
        str(shodan_api_key)
        # Crea un objeto ShodanSearch con la clave API
        shodan_search = ShodanSearch(shodan_api_key)

        # Realiza una búsqueda en Shodan
        resultados = shodan_search.search("title:dvwa", page=1)

        # Verifica que haya resultados disponibles
        if resultados is None or 'matches' not in resultados or not resultados['matches']:
            print("No se encontraron resultados.")
            return

        # Imprime detalles de los primeros 10 resultados
        for i in range(10):
            if i >= len(resultados['matches']):
                break
            resultado = resultados['matches'][i]
            print(f"\nResultado {i + 1}")
            print(f"Direccion IP: {resultado.get('ip_str', 'No disponible')}")
            print(f"Hostnames: {resultado.get('hostnames', [])}")
            print(f"Localizacion: {resultado.get('location', 'No disponible')}")

    except ValueError as e:
        raise ValueError(f"La clave API de SHODAN no es un número entero. {e}")
    except Exception as e1:
        raise ValueError(f"{type(e1)} {e1}")

if __name__ == "__main__":
    main()