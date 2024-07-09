#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <signal.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>

#define BUFFER_SIZE 1024

int server_fd = -1;  // Declarar el socket del servidor a nivel global
int new_socket = -1; // Declarar el socket del cliente a nivel global

void error(const char *msg) {
    perror(msg);
    exit(1);
}

void handle_signal(int signal) {
    printf("Recibida señal %d, cerrando el servidor...\n", signal);
    if (new_socket >= 0) {
        close(new_socket);
    }
    if (server_fd >= 0) {
        close(server_fd);
    }
    exit(0);
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Uso: %s <puerto>\n", argv[0]);
        exit(1);
    }

    int port = atoi(argv[1]);
    struct sockaddr_in address;
    socklen_t addrlen = sizeof(address);
    char buffer[BUFFER_SIZE] = {0};
    const char *hello = "Hello from server";

    // Configurar manejadores de señales
    signal(SIGINT, handle_signal);
    signal(SIGTERM, handle_signal);

    // Crear socket
    server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd < 0) {
        error("Error al abrir el socket");
    }

    // Asignar dirección y puerto
    memset(&address, 0, sizeof(address));
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(port);

    // Enlazar
    if (bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0) {
        error("Error en el binding");
    }

    // Escuchar
    if (listen(server_fd, 5) < 0) {
        error("Error en la escucha");
    }

    printf("Servidor escuchando en el puerto %d\n", port);

    // Aceptar conexión
    new_socket = accept(server_fd, (struct sockaddr *)&address, &addrlen);
    if (new_socket < 0) {
        error("Error al aceptar conexión");
    }

    printf("Conexión aceptada\n");

    while (1) {
        // Leer datos del cliente
        int valread = read(new_socket, buffer, BUFFER_SIZE);
        if (valread < 0) {
            error("Error en la lectura de datos");
        } else if (valread == 0) {
            printf("Cliente desconectado\n");
            break;
        }
        buffer[valread] = '\0';  // Asegurarse de que el buffer está null-terminated
        printf("Datos recibidos: %s\n", buffer);

        // Enviar respuesta al cliente
        if (send(new_socket, hello, strlen(hello), 0) < 0) {
            error("Error al enviar mensaje");
        }
        printf("Mensaje enviado: %s\n", hello);
    }

    // Cerrar el socket del cliente
    close(new_socket);

    // Cerrar el socket del servidor
    close(server_fd);

    return 0;
}
