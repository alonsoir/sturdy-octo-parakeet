from nessus_scanner import NessusScanner

def main():
    # Instancia del objeto NessusScanner para interactuar con Nessus
    scanner_nessus = NessusScanner()
    
    # Obtener las politicas
    scanner_nessus.get_policies()

    scanner_nessus.create_scan("1234567890", "Test Scan", "192.168.1.1")

if __name__ == "__main__":
    main()