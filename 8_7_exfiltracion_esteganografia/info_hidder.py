import cv2
import argparse
from bitarray import bitarray
import struct
import os

class ImageSteganography:
    """
    Clase para ocultar y revelar información en imágenes usando LSB (Least Significant Bit).

    Args:
        image_path (str): Ruta del archivo de imagen en la que se va a ocultar la información.
    """

    def __init__(self, image_path):
        if not os.path.isfile(image_path):
            raise FileNotFoundError(f"El archivo de imagen '{image_path}' no existe.")
        self.image = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)  # Leer la imagen sin pérdida
        self.height, self.width, self.channels = self.image.shape
        self.max_bytes = self.image.size // 8
        print(f"Máximo número de bytes a codificar: {self.max_bytes}")

    def to_binary(self, data):
        """
        Convierte datos a una representación binaria.

        Args:
            data (str o bytes): Datos a convertir a binario.

        Returns:
            bitarray: Representación binaria de los datos.
        """
        ba = bitarray()
        ba.frombytes(data.encode('utf-8') if isinstance(data, str) else data)
        return ba

    def encode(self, secret_data, output_path):
        """
        Codifica un mensaje secreto en la imagen.

        Args:
            secret_data (str): Mensaje secreto a codificar.
            output_path (str): Ruta del archivo de imagen de salida.

        Raises:
            ValueError: Si la imagen no tiene suficientes bytes para codificar el mensaje.
            UnicodeEncodeError: Si el mensaje secreto contiene caracteres no válidos en UTF-8.
        """
        try:
            secret_data_bytes = secret_data.encode('utf-8')
        except UnicodeEncodeError:
            raise UnicodeEncodeError("El mensaje secreto contiene caracteres no válidos en UTF-8.")

        secret_data_with_marker = f"{secret_data_bytes.decode('utf-8')}===="
        data_length = len(secret_data_with_marker)

        # Empaquetar la longitud del mensaje en los primeros 4 bytes
        length_bytes = struct.pack('>I', data_length)
        binary_data = self.to_binary(length_bytes + secret_data_with_marker.encode('utf-8'))

        if len(binary_data) > self.max_bytes * 8:
            raise ValueError("Bytes insuficientes, se necesita una imagen más grande.")

        data_index = 0
        for y in range(self.height):
            for x in range(self.width):
                for c in range(self.channels):
                    if data_index >= len(binary_data):
                        break
                    bit = binary_data[data_index]
                    self.image[y, x, c] = (self.image[y, x, c] & 0b11111110) | bit
                    data_index += 1
                if data_index >= len(binary_data):
                    break

        cv2.imwrite(output_path, self.image)
        print(f"Imagen codificada guardada en '{output_path}'.")

    def decode(self):
        """
        Decodifica el mensaje secreto de la imagen.

        Returns:
            str: Mensaje secreto decodificado.

        Raises:
            ValueError: Si la imagen no contiene un mensaje codificado válido.
        """
        binary_data = bitarray()
        binary_data.extend((pixel & 1 for pixel in self.image.reshape(-1, self.channels).ravel()))

        # Leer la longitud del mensaje
        length_bytes = binary_data[:32]  # 4 bytes = 32 bits
        try:
            data_length = struct.unpack('>I', length_bytes.tobytes())[0]
        except struct.error:
            raise ValueError("La imagen no contiene un mensaje codificado válido.")

        secret_data = binary_data[32:32 + data_length * 8].tobytes().decode('utf-8', errors='replace')
        marker_index = secret_data.find("====")
        if marker_index == -1:
            raise ValueError("La imagen no contiene un mensaje codificado válido.")

        return secret_data[:marker_index]

def main():
    """
    Función principal para manejar la codificación y decodificación de mensajes en imágenes.
    """
    parser = argparse.ArgumentParser(description="Codifica y decodifica mensajes secretos en imágenes.")
    parser.add_argument("action", choices=["encode", "decode"], help="Elige entre 'encode' o 'decode'.")
    parser.add_argument("input_path", help="Ruta del archivo de imagen de entrada.")
    parser.add_argument("--secret-data", help="Mensaje secreto a codificar")
    parser.add_argument("--output-path", help="Ruta del archivo de imagen de salida.")

    args = parser.parse_args()

    steganography = ImageSteganography(args.input_path)

    try:
        if args.action == 'encode':
            if not args.secret_data:
                parser.error("Debe proporcionar un mensaje secreto a codificar.")
            steganography.encode(args.secret_data, args.output_path or "encoded_image.png")
        elif args.action == 'decode':
            decoded_data = steganography.decode()
            print(f"Datos decodificados: {decoded_data}")
    except (ValueError, OSError, UnicodeEncodeError) as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
