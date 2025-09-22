# server.py
import os
import time
import numpy as np
from enlace import enlace
from pacote import Pacote
from txtgen import escreve

SERIAL_SERVER = "COM6"
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
