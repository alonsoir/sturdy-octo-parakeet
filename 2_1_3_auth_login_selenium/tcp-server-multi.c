#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <signal.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <pthread.h>
#include <errno.h>

#define BUFFER_SIZE 1024
#define MAX_CLIENTS 1000

int server_fd = -1;
volatile sig_atomic_t keep_running = 1;

void error(const char *msg) {
    perror(msg);
    exit(1);
}

void handle_signal(int signal) {
    printf("Recibida señal %d, cerrando el servidor...\n", signal);
    keep_running = 0;
}

void *handle_client(void *arg) {
    int new_socket = *((int *)arg);
    free(arg);

    char buffer[BUFFER_SIZE] = {0};
    const char *hello = "Hello from server";

    printf("Conexión aceptada\n");

    while (keep_running) {
        int valread = recv(new_socket, buffer, BUFFER_SIZE - 1, 0);
        if (valread < 0) {
            if (errno == EINTR) continue;
            perror("Error en la lectura de datos");
            break;
        } else if (valread == 0) {
            printf("Cliente desconectado\n");
            break;
        }
        buffer[valread] = '\0';
        printf("Datos recibidos: %s\n", buffer);

        if (strcmp(buffer, "CLOSE") == 0) {
            printf("Cliente solicitó cerrar la conexión\n");
            break;
        }

        if (send(new_socket, hello, strlen(hello), 0) < 0) {
            perror("Error al enviar mensaje");
            break;
        }
        printf("Mensaje enviado: %s\n", hello);
    }

    close(new_socket);
    return NULL;
}

int main(int argc, char *argv[]) {
    if (argc != 2) {
        fprintf(stderr, "Uso: %s <puerto>\n", argv[0]);
        exit(1);
    }

    int port = atoi(argv[1]);
    struct sockaddr_in address;
    socklen_t addrlen = sizeof(address);

    signal(SIGINT, handle_signal);
    signal(SIGTERM, handle_signal);

    server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server_fd < 0) {
        error("Error al abrir el socket");
    }

    int opt = 1;
    if (setsockopt(server_fd, SOL_SOCKET, SO_REUSEADDR, &opt, sizeof(opt))) {
        error("Error en setsockopt");
    }

    memset(&address, 0, sizeof(address));
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(port);

    if (bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0) {
        error("Error en el binding");
    }

    if (listen(server_fd, MAX_CLIENTS) < 0) {
        error("Error en la escucha");
    }

    printf("Servidor escuchando en el puerto %d\n", port);

    while (keep_running) {
        int *new_socket = malloc(sizeof(int));
        if (new_socket == NULL) {
            error("Error en la asignación de memoria");
        }

        *new_socket = accept(server_fd, (struct sockaddr *)&address, &addrlen);
        if (*new_socket < 0) {
            if (errno == EINTR) {
                free(new_socket);
                continue;
            }
            free(new_socket);
            perror("Error al aceptar conexión");
            continue;
        }

        pthread_t thread_id;
        if (pthread_create(&thread_id, NULL, handle_client, (void *)new_socket) != 0) {
            free(new_socket);
            perror("Error al crear hilo");
            continue;
        }

        pthread_detach(thread_id);
    }

    close(server_fd);
    return 0;
}