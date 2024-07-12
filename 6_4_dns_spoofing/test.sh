#!/bin/bash

# Lista de dominios a consultar
domains=("facebook.com" "google.com" "example.com")

# Función para realizar la consulta DNS y verificar la respuesta
check_dns_response() {
    domain=$1
    expected_ip=$2

    echo "Consultando DNS para el dominio: $domain"

    # Realizar la consulta DNS usando 'dig'
    actual_ip=$(dig +short @localhost $domain)

    echo "Respuesta DNS recibida: $actual_ip"

    # Comparar la respuesta recibida con la IP esperada
    if [ "$actual_ip" == "$expected_ip" ]; then
        echo "✅ La respuesta recibida para $domain es la esperada: $actual_ip"
    else
        echo "❌ La respuesta recibida para $domain NO es la esperada: $actual_ip"
    fi
}

# Recorrer la lista de dominios y realizar la comprobación
for domain in "${domains[@]}"; do
    check_dns_response $domain "192.168.1.37"
    echo "--------------------------------------"
done
