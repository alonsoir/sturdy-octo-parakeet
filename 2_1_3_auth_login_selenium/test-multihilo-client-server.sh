#!/bin/bash

# Puerto del servidor
PORT=8080

# Número de hilos (peticiones concurrentes)
NUM_THREADS=100

# Dirección IP del servidor (localhost en este caso)
SERVER_IP="127.0.0.1"

# Duración de cada conexión en segundos
DURATION=30

# Función para verificar si el puerto está en uso
check_port() {
    if lsof -i :$1 | grep LISTEN; then
        echo "El puerto $1 está en uso. Por favor, elija otro puerto."
        exit 1
    fi
}

# Verificar si el puerto está disponible
check_port $PORT

# Compilar el servidor y el cliente
gcc -o tcp-server-multi tcp-server-multi.c -lpthread
gcc -o tcp-client-multi tcp-client-multi.c -lpthread

# Iniciar el servidor en segundo plano y capturar su salida
./tcp-server-multi $PORT > server_output.log 2>&1 &
SERVER_PID=$!

# Esperar y verificar que el servidor esté escuchando
for i in {1..10}; do
    if lsof -i :$PORT | grep LISTEN; then
        echo "Servidor iniciado y escuchando en el puerto $PORT"
        break
    fi
    if [ $i -eq 10 ]; then
        echo "Error: El servidor no se inició correctamente"
        echo "Contenido de server_output.log:"
        cat server_output.log
        if ps -p $SERVER_PID > /dev/null; then
            kill $SERVER_PID
        fi
        exit 1
    fi
    sleep 1
done

# Ejecutar el cliente con múltiples hilos
./tcp-client-multi $SERVER_IP $PORT $NUM_THREADS $DURATION

# Esperar a que todas las conexiones se cierren
sleep 5

echo "Prueba completada. El servidor sigue en ejecución."
echo "Para detener el servidor, ejecute: kill $SERVER_PID"