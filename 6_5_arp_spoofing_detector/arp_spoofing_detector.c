#include <stdio.h>
#include <stdlib.h>
#include <pcap.h>
#include <arpa/inet.h>
#include <string.h>
#include <net/ethernet.h>
#include <netinet/if_ether.h>
#include <netinet/ip.h>
#include <ifaddrs.h>
#include <net/if.h>
#include <net/if_dl.h>
#include <unistd.h>

#define MAX_IP_LENGTH 16
#define MAX_MAC_LENGTH 18

// Obtiene la dirección MAC de una interfaz
void get_mac_address(const char* ifname, char* mac) {
    struct ifaddrs *ifap, *ifa;
    unsigned char *ptr;

    if (getifaddrs(&ifap) != 0) {
        perror("getifaddrs");
        exit(EXIT_FAILURE);
    }

    for (ifa = ifap; ifa != NULL; ifa = ifa->ifa_next) {
        if (ifa->ifa_addr && ifa->ifa_addr->sa_family == AF_LINK && strcmp(ifa->ifa_name, ifname) == 0) {
            ptr = (unsigned char *)LLADDR((struct sockaddr_dl *)ifa->ifa_addr);
            snprintf(mac, MAX_MAC_LENGTH, "%02x:%02x:%02x:%02x:%02x:%02x", ptr[0], ptr[1], ptr[2], ptr[3], ptr[4], ptr[5]);
            break;
        }
    }

    freeifaddrs(ifap);
}

// Obtiene la dirección IP de una interfaz
void get_ip_address(const char* ifname, char* ip) {
    struct ifaddrs *ifap, *ifa;

    if (getifaddrs(&ifap) != 0) {
        perror("getifaddrs");
        exit(EXIT_FAILURE);
    }

    for (ifa = ifap; ifa != NULL; ifa = ifa->ifa_next) {
        if (ifa->ifa_addr && ifa->ifa_addr->sa_family == AF_INET && strcmp(ifa->ifa_name, ifname) == 0) {
            struct sockaddr_in* sa = (struct sockaddr_in*)ifa->ifa_addr;
            snprintf(ip, MAX_IP_LENGTH, "%s", inet_ntoa(sa->sin_addr));
            break;
        }
    }

    freeifaddrs(ifap);
}

// Callback que se llama por cada paquete capturado
void packet_handler(u_char *args, const struct pcap_pkthdr *header, const u_char *packet) {
    char *ifname = (char *)args; // Hacer el casting a char *
    struct ether_header *eth_hdr = (struct ether_header *)packet;
    struct ether_arp *arp_hdr = (struct ether_arp *)(packet + sizeof(struct ether_header));

    if (ntohs(eth_hdr->ether_type) == ETHERTYPE_ARP) {
        if (ntohs(arp_hdr->ea_hdr.ar_op) == ARPOP_REPLY) {
            char sender_ip[MAX_IP_LENGTH];
            char sender_mac[MAX_MAC_LENGTH];

            snprintf(sender_ip, MAX_IP_LENGTH, "%d.%d.%d.%d",
                     arp_hdr->arp_spa[0], arp_hdr->arp_spa[1],
                     arp_hdr->arp_spa[2], arp_hdr->arp_spa[3]);
            snprintf(sender_mac, MAX_MAC_LENGTH, "%02x:%02x:%02x:%02x:%02x:%02x",
                     arp_hdr->arp_sha[0], arp_hdr->arp_sha[1],
                     arp_hdr->arp_sha[2], arp_hdr->arp_sha[3],
                     arp_hdr->arp_sha[4], arp_hdr->arp_sha[5]);

            char real_mac[MAX_MAC_LENGTH];
            get_mac_address(ifname, real_mac); // Usar ifname directamente

            if (strcmp(sender_mac, real_mac) != 0) {
                printf("[ALERTA] Estás bajo un ataque ARP Spoofing. IP: %s, MAC FALSA: %s, MAC REAL: %s\n", sender_ip, sender_mac, real_mac);
            }
        }
    }
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Uso: %s <interfaz>\n", argv[0]);
        return 1;
    }

    char errbuf[PCAP_ERRBUF_SIZE];
    pcap_t *handle;

    handle = pcap_open_live(argv[1], BUFSIZ, 1, 1000, errbuf);
    if (handle == NULL) {
        fprintf(stderr, "No se pudo abrir la interfaz %s: %s\n", argv[1], errbuf);
        return 2;
    }
    pcap_loop(handle, 0, packet_handler, argv[1]);

    pcap_close(handle);
    return 0;
}