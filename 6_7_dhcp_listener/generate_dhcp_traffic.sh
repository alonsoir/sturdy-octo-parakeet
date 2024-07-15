#!/bin/bash

# Pedir al usuario que ingrese la interfaz de red
read -p "Ingrese la interfaz de red a utilizar: " INTERFACE

# Enviar un paquete DHCP DISCOVER
echo "Enviando paquete DHCP DISCOVER..."
sudo ipconfig set "$INTERFACE" DHCP

# Esperar un momento
sleep 5

# Enviar un paquete DHCP REQUEST
echo "Enviando paquete DHCP REQUEST..."
sudo ipconfig set "$INTERFACE" DHCP

# Esperar otro momento
sleep 5

# Liberar la dirección IP
echo "Liberando la dirección IP..."
sudo ipconfig set "$INTERFACE" MANUAL 0.0.0.0 0.0.0.0