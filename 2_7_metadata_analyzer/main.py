from metadata_analyzer import extract_metadata

def display_metadata(filepath):
    """Extrae y muestra los metadatos de un archivo.

    Args:
        filepath (str): Ruta del archivo del cual se extraerán los metadatos.
    """
    try:
        metadata = extract_metadata(filepath)
        for key, value in metadata.items():
            print(f"{key}: {value}")
    except FileNotFoundError:
        print("Error: El archivo especificado no fue encontrado.")
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Error inesperado: {e}")


if __name__ == "__main__":
    filepath = "/Users/aironman/git/shodan-Santiago/2_7_metadata_analyzer/Hoja de fórmulas.pdf"
    display_metadata(filepath)