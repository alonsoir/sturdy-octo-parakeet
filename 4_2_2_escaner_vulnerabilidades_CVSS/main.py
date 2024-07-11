import json

from vulnerability_scanner import VulnerabilityScanner


if __name__ == "__main__":
    scanner = VulnerabilityScanner()
    servicio = "ProFTPD 1.3.5"
    cves_encontrados = scanner.search_cves(servicio)
    # Formatear y mostrar el JSON de manera legible
    formatted_json = json.dumps(cves_encontrados, indent=4, ensure_ascii=False)
    print(formatted_json)