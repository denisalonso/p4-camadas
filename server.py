# server.py
import os
import time
import numpy as np
from enlace import enlace
from pacote import Pacote
from txtgen import escreve

SERIAL_SERVER = "COM14"
ARQUIVO_SAIDA = "saida.png"

def main():
    com = enlace(SERIAL_SERVER)
    p = Pacote()
    try:
        com.enable()
        print(f"[SRV] Porta aberta: {SERIAL_SERVER}")

        # Byte de sacrifício
        rx, _ = com.getData(1)
        com.rx.clearBuffer()
        time.sleep(0.1)

        recebidos = {}
        total = None

        while True:
            seq, total, plen, crc, payload = p.recebe_pacote(com, timeout=15)

            escreve("server_log.txt", "receb", plen, seq, total, crc)

            if p.calcula_crc16(payload) != crc:
                print(f"[SRV] Erro CRC no pacote {seq}, enviando NAK")
                com.sendData(b"\x00")
                escreve("server_log.txt", "envio", 0, seq, total, 0)
                continue

            recebidos[seq] = payload
            com.sendData(b"\x01")
            escreve("server_log.txt", "envio", 0, seq, total, crc)
            print(f"[SRV] Pacote {seq+1}/{total} recebido OK")

            if len(recebidos) == total:
                break

        # Junta e salva
        with open(ARQUIVO_SAIDA, "wb") as f:
            for i in range(total):
                f.write(recebidos[i])

        print("[SRV] Arquivo salvo com sucesso!")

    finally:
        com.disable()
        print("[SRV] fim")

if __name__ == "__main__":
    main()

#Traceback (most recent call last):
#   File "c:\Users\dedal\OneDrive\Área de Trabalho\camadas\p4-camadas\server.py", line 16, in main
#     com.enable()
#     ~~~~~~~~~~^^
#   File "c:\Users\dedal\OneDrive\Área de Trabalho\camadas\p4-camadas\enlace.py", line 29, in enable
#     self.fisica.open()
#     ~~~~~~~~~~~~~~~~^^
#   File "c:\Users\dedal\OneDrive\Área de Trabalho\camadas\p4-camadas\interfaceFisica.py", line 31, in open
#     self.port = serial.Serial(self.name,
#                 ~~~~~~~~~~~~~^^^^^^^^^^^
#                               self.baudrate,
#                               ^^^^^^^^^^^^^^
#     ...<2 lines>...
#                               self.stop,
#                               ^^^^^^^^^^
#                               self.timeout)
#                               ^^^^^^^^^^^^^
#   File "C:\Users\dedal\AppData\Local\Programs\Python\Python313\Lib\site-packages\serial\serialwin32.py", line 33, in __init__
#     super(Serial, self).__init__(*args, **kwargs)
#     ~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^
#   File "C:\Users\dedal\AppData\Local\Programs\Python\Python313\Lib\site-packages\serial\serialutil.py", line 244, in __init__
#     self.open()
#     ~~~~~~~~~^^
#   File "C:\Users\dedal\AppData\Local\Programs\Python\Python313\Lib\site-packages\serial\serialwin32.py", line 64, in open
#     raise SerialException("could not open port {!r}: {!r}".format(self.portstr, ctypes.WinError()))
# serial.serialutil.SerialException: could not open port 'COM8': FileNotFoundError(2, 'O sistema não pode encontrar o arquivo especificado.', None, 2)

# During handling of the above exception, another exception occurred:

# Traceback (most recent call last):
#   File "c:\Users\dedal\OneDrive\Área de Trabalho\camadas\p4-camadas\server.py", line 58, in <module>
#     main()
#     ~~~~^^
#   File "c:\Users\dedal\OneDrive\Área de Trabalho\camadas\p4-camadas\server.py", line 54, in main
#     com.disable()
#     ~~~~~~~~~~~^^
#   File "c:\Users\dedal\OneDrive\Área de Trabalho\camadas\p4-camadas\enlace.py", line 37, in disable
#     self.fisica.close()
#     ~~~~~~~~~~~~~~~~~^^
#   File "c:\Users\dedal\OneDrive\Área de Trabalho\camadas\p4-camadas\interfaceFisica.py", line 40, in close
#     self.port.close()
#     ^^^^^^^^^^^^^^^
# AttributeError: 'NoneType' object has no attribute 'close'
# PS C:\Users\dedal\OneDrive\Área de Trabalho\camadas\p4-camadas>


















