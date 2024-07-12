# LINUX

Ejecuta el siguiente comando para redirigir el tráfico DNS a tu script (necesitarás privilegios de administrador):

    sudo pfctl -e
    echo "rdr pass on lo0 inet proto udp from any to any port 53 -> 127.0.0.1 port 53" | sudo pfctl -f -

Modifica el archivo /etc/resolv.conf para usar tu DNS local:

    sudo echo "nameserver 127.0.0.1" > /etc/resolv.conf

Ejecuta tu script con privilegios de root:

    sudo python3 dns_spoofer.py

Ahora, cuando ejecutes tu script de prueba bash, deberías ver las respuestas DNS spoofed.

Después de terminar las pruebas, no olvides revertir los cambios:

    sudo pfctl -F all -f /etc/pf.conf
    sudo pfctl -d

Y restaura tu archivo /etc/resolv.conf a su estado original.
Recuerda que realizar DNS spoofing sin autorización puede ser ilegal y éticamente cuestionable. 
Asegúrate de solo realizar estas pruebas en un entorno controlado y con permiso.

# OSX

En macOS moderno, el archivo /etc/resolv.conf no se usa para la configuración de DNS. 
En su lugar, macOS utiliza el servicio de directorio para manejar la configuración de DNS. 
Vamos a modificar nuestro enfoque para que funcione en macOS:

En lugar de modificar /etc/resolv.conf, vamos a usar networksetup para cambiar los servidores DNS.
Necesitaremos saber el nombre de la interfaz de red que estás usando (por ejemplo, Wi-Fi o Ethernet).

Aquí tienes los pasos actualizados:

Primero, identifica tu interfaz de red activa:
    
    networksetup -listallnetworkservices

Esto te dará una lista de tus servicios de red. Identifica el que estás usando (probablemente "Wi-Fi" o "Ethernet").
Guarda tus servidores DNS actuales para poder restaurarlos después:

    networksetup -getdnsservers Wi-Fi > original_dns_servers.txt

(Reemplaza "Wi-Fi" con el nombre de tu interfaz si es diferente)

Configura tu máquina para usar tu servidor DNS local:

    sudo networksetup -setdnsservers Wi-Fi 127.0.0.1

Ejecuta los comandos para redirigir el tráfico DNS:

    sudo pfctl -e
    echo "rdr pass on lo0 inet proto udp from any to any port 53 -> 127.0.0.1 port 53" | sudo pfctl -f -

Ejecuta tu script de Python con privilegios de root:

    sudo python3 dns_spoofer.py

Ahora puedes ejecutar tu script de prueba bash y deberías ver las respuestas DNS spoofed.
Cuando hayas terminado, restaura tu configuración original:
    
    sudo pfctl -F all -f /etc/pf.conf
    sudo pfctl -d
    sudo networksetup -setdnsservers Wi-Fi $(cat original_dns_servers.txt)


Recuerda reemplazar "Wi-Fi" con el nombre de tu interfaz de red si es diferente.
También, asegúrate de que tu script Python esté escuchando en el puerto 53 y tenga los permisos necesarios para hacerlo.
Por último, ten en cuenta que estas modificaciones afectarán a toda la resolución DNS de tu sistema. 
Asegúrate de realizar estas pruebas en un entorno controlado y ten cuidado de no interrumpir tus conexiones de red 
normales.