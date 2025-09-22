# # server.py
# import os
# import time
# import numpy as np
# from enlace import enlace
# from pacote import Pacote
# from txtgen import escreve

# SERIAL_SERVER = "COM7"
# ARQUIVO_SAIDA = "saida.png"

# def main():
#     com = enlace(SERIAL_SERVER)
#     p = Pacote()
#     try:
#         com.enable()
#         print(f"[SRV] Porta aberta: {SERIAL_SERVER}")

#         # Byte de sacrifício
#         rx, _ = com.getData(1)
#         com.rx.clearBuffer()
#         time.sleep(0.1)

#         recebidos = {}
#         total = None

#         # while True:
#         #     seq, total, plen, crc, payload = p.recebe_pacote(com, timeout=15)

#         #     escreve("server_log.txt", "receb", plen, seq, total, crc)

#         #     if p.calcula_crc16(payload) != crc:
#         #         print(f"[SRV] Erro CRC no pacote {seq}, enviando NAK")
#         #         com.sendData(b"\x00")
#         #         escreve("server_log.txt", "envio", 0, seq, total, 0)
#         #         continue

#         #     recebidos[seq] = payload
#         #     com.sendData(b"\x01")
#         #     escreve("server_log.txt", "envio", 0, seq, total, crc)
#         #     print(f"[SRV] Pacote {seq+1}/{total} recebido OK")

#         #     if len(recebidos) == total:
#         #         break
#         esperado = 0
#         recebidos = {}
#         total = None

#         while True:
#             seq, total, plen, crc, payload = p.recebe_pacote(com, timeout=15)
#             escreve("server_log.txt", "receb", plen, seq, total, crc)

#             if p.calcula_crc16(payload) != crc:
#                 print(f"[SRV] Erro CRC no pacote {seq}, enviando NAK")
#                 com.sendData(b"\x00")   # NAK
#                 escreve("server_log.txt", "envio", 0, seq, total, 0)
#                 continue

#             if seq != esperado:
#                 print(f"[SRV] Fora de ordem! Esperava {esperado}, recebi {seq}. Mandando NAK.")
#                 com.sendData(b"\x00")   # NAK
#                 escreve("server_log.txt", "envio", 0, seq, total, 0)
#                 continue

#             # Se chegou aqui: pacote certo
#             recebidos[seq] = payload
#             com.sendData(b"\x01")  # ACK
#             escreve("server_log.txt", "envio", 0, seq, total, crc)
#             print(f"[SRV] Pacote {seq+1}/{total} recebido OK")

#             esperado += 1

#             if len(recebidos) == total:
#                 break

#         # Junta e salva
#         with open(ARQUIVO_SAIDA, "wb") as f:
#             for i in range(total):
#                 f.write(recebidos[i])

#         print("[SRV] Arquivo salvo com sucesso!")

#     finally:
#         com.disable()
#         print("[SRV] fim")

# if __name__ == "__main__":
#     main()
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

        esperado = 0
        recebidos = {}
        total = None

        while True:
            seq, total, plen, crc, payload = p.recebe_pacote(com, timeout=15)
            escreve("server_log.txt", "receb", plen, seq, total, crc)

            # Verifica CRC
            if p.calcula_crc16(payload) != crc:
                print(f"[SRV] Erro CRC no pacote {seq}, enviando NAK")
                com.sendData(b"\x00")
                escreve("server_log.txt", "envio", 0, seq, total, 0)
                continue

            # Verifica ordem
            if seq != esperado:
                print(f"[SRV] Fora de ordem! Esperava {esperado}, recebi {seq}. Reenviando ACK do último válido.")
                # ACK do último válido (esperado-1)
                ultimo_valido = max(0, esperado-1)
                com.sendData(b"\x01")
                escreve("server_log.txt", "envio", 0, ultimo_valido, total, 0)
                continue

            # Pacote correto
            recebidos[seq] = payload
            com.sendData(b"\x01")
            escreve("server_log.txt", "envio", 0, seq, total, crc)
            print(f"[SRV] Pacote {seq+1}/{total} recebido OK")
            esperado += 1

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
