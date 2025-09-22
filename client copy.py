# client.py
import os
import random as rd
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

        # Lê arquivo inteiro
        with open(ARQUIVO, "rb") as f:
            data = f.read()

        total = (len(data) + p.MAX_PAY - 1) // p.MAX_PAY
        lista_erro = []

        # Cria todos os pacotes em ordem correta
        for i in range(total):
            start = i * p.MAX_PAY
            end = start + p.MAX_PAY
            payload = data[start:end]
            pacote = p.cria_pacote(i, total, payload)
            crc = p.calcula_crc16(payload)
            lista_erro.append((pacote, payload, i, crc))

        # Embaralha a lista para simular erro de ordem
        rd.shuffle(lista_erro)

        # Envia na ordem embaralhada
        for pacote, payload, j, crc in lista_erro:
            com.sendData(np.asarray(pacote))
            escreve("client_log.txt", "envio", len(payload), j, total, crc)
            print(f"[CLI] Pacote {j+1}/{total} enviado (fora de ordem)")

            # Espera ACK/NAK
            rx, _ = com.getData(1)
            if rx == b"\x01":
                print(f"[CLI] ACK recebido ({j+1}/{total})")
                escreve("client_log.txt", "receb", 0, j, total, crc)
            else:
                print(f"[CLI] NAK recebido, reenviando {j+1}")
                escreve("client_log.txt", "receb", 0, j, total, crc)
                com.sendData(np.asarray(pacote))  # reenvio imediato

        print("[CLI] Transmissão concluída!")

    finally:
        com.disable()
        print("[CLI] fim")

if __name__ == "__main__":
    main()
