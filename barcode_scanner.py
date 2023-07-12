from pyzbar import pyzbar
import cv2
import time
from google_api import *


def try_parse_int(id_barcode):
    try:
        id_as_int = int(id_barcode)
        return True, id_as_int
    except ValueError:
        return False, None


# Inicia la cámara para la captura
camera = cv2.VideoCapture(0)  # 0 -> index / Default camara de multiples

scanner = True
COOLDOWN_PERIOD = 7
last_scan_time = None
last_scan_data = None
while scanner:
    # Tomar Frame de camara a analizar
    # bool tryout (¿regreso imagen o no?)
    # mat frame (imagen en formato de matriz)
    tryout, frame = camera.read()

    # Conversión de frame a escala de grises para la detección)
    grayFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Identificar y decodificar el código de barras
    barcodes = pyzbar.decode(grayFrame)  # Escanea múltiples barcodes (regresa Lista)

    # Si Lista-Vacía no decodifica (no hay barcode)
    if barcodes:
        current_time = time.time()
        if last_scan_time is not None and current_time - last_scan_time < COOLDOWN_PERIOD:
            pass
        else:
            last_scan_time = current_time

            barcode = barcodes[0]  # Solo importa el 1er barcode *(Posible error con múltiples?)
            data = barcode.data.decode("utf-8")  # Decodifica valor contenido en UTF-8
            barcodeType = barcode.type  # Decodifica Typo de código de barras
            if data == last_scan_data:
                # Mismo código que el anterior así YA escaneado, por tanto Saltarlo
                pass
            else:
                last_scan_data = data

                is_valid, id_data = try_parse_int(data)
                if is_valid:
                    id_index = get_id_index(id_data)
                    if is_expired(id_index):
                        print('Código ya no es válido')
                    else:
                        update_static_data(id_index)
                        update_dynamic_data()
                else:
                    print(f"Error en valor escaneado {data}, Reintente otra vez")

            # QUITAR AL FINAL
            cv2.putText(frame, f"{barcodeType}: {data}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

    cv2.imshow("Barcode Scanner", frame)    # Nombre ventana y Mostrar la cámara

    # Detener código al presionar letra 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

camera.release()    # Asegurar apagado correcto de camara
cv2.destroyAllWindows()  # Cerrar pestaña creada para la camara
