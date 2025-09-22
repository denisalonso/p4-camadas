# client.py
import os
import time
import numpy as np
from enlace import enlace
from pacote import Pacote
from txtgen import escreve

SERIAL_CLIENT = "COM7"
ARQUIVO = "image.png"

def main():
    com = enlace(SERIAL_CLIENT)
    p = Pacote()
    try:
        com.enable()
        print(f"[CLI] Porta aberta: {SERIAL_CLIENT}")

        # Byte de sacrifício
        com.sendData(b"00")
        time.sleep(0.2)

        with open(ARQUIVO, "rb") as f:
            data = f.read()

        total = (len(data) + p.MAX_PAY - 1) // p.MAX_PAY

        i = 0
        while i < total:
            if i ==5:
                i=6
            start = i * p.MAX_PAY
            end = start + p.MAX_PAY
            payload = data[start:end]
            pacote = p.cria_pacote(i, total, payload)
            crc = p.calcula_crc16(payload)

            com.sendData(np.asarray(pacote))
            escreve("client_log.txt", "envio", len(payload), i, total, crc)
            print(f"[CLI] Pacote {i+1}/{total} enviado")

            rx, _ = com.getData(1)
            if rx == b"\x01":
                print(f"[CLI] ACK recebido ({i+1}/{total})")
                escreve("client_log.txt", "receb", 0, i, total, crc)
                i += 1
            else:
                print(f"[CLI] NAK recebido, reenviando {i+1}")
                escreve("client_log.txt", "receb", 0, i, total, crc)

        print("[CLI] Transmissão concluída!")

    finally:
        com.disable()
        print("[CLI] fim")

if __name__ == "__main__":
    main()
