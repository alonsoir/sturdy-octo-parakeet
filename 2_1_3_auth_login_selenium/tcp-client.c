#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#define BUFFER_SIZE 1024

void error(const char *msg) {
    perror(msg);
    exit(1);
}

int main(int argc, char *argv[]) {
    if (argc != 3) {
        fprintf(stderr, "Uso: %s <direccion IP> <puerto>\n", argv[0]);
        exit(1);
    }

    const char *server_ip = argv[1];
    int port = atoi(argv[2]);
    int sock = 0;
    struct sockaddr_in serv_addr;
    char buffer[BUFFER_SIZE] = {0};

    // Crear socket
    if ((sock = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
        error("Error al crear el socket");
    }

    // Configurar dirección del servidor
    memset(&serv_addr, 0, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(port);

    // Convertir dirección IP de texto a binario
    if (inet_pton(AF_INET, server_ip, &serv_addr.sin_addr) <= 0) {
        error("Dirección no válida / Dirección no soportada");
    }

    // Conectar al servidor
    if (connect(sock, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0) {
        error("Conexión fallida");
    }

    printf("Conectado al servidor %s en el puerto %d\n", server_ip, port);

    while (1) {
        printf("Ingrese el mensaje (o 'salir' para terminar): ");
        if (fgets(buffer, BUFFER_SIZE, stdin) == NULL) {
            printf("Error al leer la entrada\n");
            break;
        }

        // Remover el salto de línea
        size_t len = strlen(buffer);
        if (len > 0 && buffer[len-1] == '\n') {
            buffer[len-1] = '\0';
            len--;
        }

        // Salir si el mensaje es 'salir'
        if (strcmp(buffer, "salir") == 0) {
            printf("Cerrando conexión...\n");
            break;
        }

        // Verificar si el mensaje no está vacío
        if (len == 0) {
            printf("Mensaje vacío, por favor ingrese un mensaje.\n");
            continue;
        }

        // Enviar mensaje al servidor
        if (send(sock, buffer, len, 0) < 0) {
            error("Error al enviar mensaje");
        }

        // Limpiar el buffer para recibir la respuesta
        memset(buffer, 0, BUFFER_SIZE);

        // Leer respuesta del servidor
        int valread = read(sock, buffer, BUFFER_SIZE);
        if (valread < 0) {
            error("Error en la lectura de datos");
        } else if (valread == 0) {
            printf("El servidor cerró la conexión\n");
            break;
        }
        printf("Respuesta del servidor: %s\n", buffer);

        // Limpiar el buffer para el siguiente mensaje
        memset(buffer, 0, BUFFER_SIZE);
    }

    // Cerrar el socket
    close(sock);

    return 0;
}
