#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <pthread.h>
#include <errno.h>
#include <time.h>

#define BUFFER_SIZE 1024

typedef struct {
    char server_ip[INET_ADDRSTRLEN];
    int port;
    int duration;
} thread_args_t;

void error(const char *msg) {
    perror(msg);
    exit(1);
}

void *client_thread(void *arg) {
    thread_args_t *args = (thread_args_t *)arg;
    char buffer[BUFFER_SIZE] = {0};
    time_t start_time = time(NULL);

    int sock = 0;
    struct sockaddr_in serv_addr;

    if ((sock = socket(AF_INET, SOCK_STREAM, 0)) < 0) {
        error("Error al crear el socket");
    }

    memset(&serv_addr, 0, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(args->port);

    if (inet_pton(AF_INET, args->server_ip, &serv_addr.sin_addr) <= 0) {
        error("Dirección no válida / Dirección no soportada");
    }

    if (connect(sock, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) < 0) {
        error("Conexión fallida");
    }

    printf("Conectado al servidor %s en el puerto %d\n", args->server_ip, args->port);

    while (time(NULL) - start_time < args->duration) {
        snprintf(buffer, BUFFER_SIZE, "Mensaje desde el hilo %p", (void*)pthread_self());

        if (send(sock, buffer, strlen(buffer), 0) < 0) {
            error("Error al enviar mensaje");
        }

        memset(buffer, 0, BUFFER_SIZE);

        int valread = recv(sock, buffer, BUFFER_SIZE - 1, 0);
        if (valread < 0) {
            if (errno == EINTR) {
                printf("Lectura interrumpida, reintentando...\n");
            } else {
                perror("Error en la lectura de datos");
            }
        } else if (valread == 0) {
            printf("El servidor cerró la conexión\n");
            break;
        } else {
            buffer[valread] = '\0';
            printf("Respuesta del servidor: %s\n", buffer);
        }

        sleep(1);  // Esperar 1 segundo antes de enviar el siguiente mensaje
    }

    // Enviar mensaje de cierre
    strcpy(buffer, "CLOSE");
    if (send(sock, buffer, strlen(buffer), 0) < 0) {
        error("Error al enviar mensaje de cierre");
    }

    close(sock);
    free(arg);
    return NULL;
}

int main(int argc, char *argv[]) {
    if (argc != 5) {
        fprintf(stderr, "Uso: %s <direccion IP> <puerto> <numero de hilos> <duración en segundos>\n", argv[0]);
        exit(1);
    }

    char *server_ip = argv[1];
    int port = atoi(argv[2]);
    int num_threads = atoi(argv[3]);
    int duration = atoi(argv[4]);

    pthread_t threads[num_threads];

    for (int i = 0; i < num_threads; i++) {
        thread_args_t *args = malloc(sizeof(thread_args_t));
        if (!args) {
            error("Error al asignar memoria");
        }
        strncpy(args->server_ip, server_ip, INET_ADDRSTRLEN);
        args->port = port;
        args->duration = duration;

        if (pthread_create(&threads[i], NULL, client_thread, (void *)args) != 0) {
            error("Error al crear hilo");
        }
    }

    for (int i = 0; i < num_threads; i++) {
        pthread_join(threads[i], NULL);
    }

    return 0;
}