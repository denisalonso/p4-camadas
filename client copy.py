# client.py
import time
import numpy as np
from enlace import enlace
from pacote import Pacote
from txtgen import escreve

SERIAL_CLIENT = "COM7"      # <-- use a porta do Arduino do CLIENTE
ARQUIVO = "maior.png"

def main():
    com = enlace(SERIAL_CLIENT)
    p = Pacote()
    try:
        com.enable()
        print(f"[CLI] Porta aberta: {SERIAL_CLIENT}")

        # Byte de sacrifício
        com.sendData(b"00")
        time.sleep(0.2)

        # Carrega arquivo
        with open(ARQUIVO, "rb") as f:
            data = f.read()

        total = (len(data) + p.MAX_PAY - 1) // p.MAX_PAY

        i = 0
        erro_injetado = False  # garante que só pulamos uma vez

        while i < total:
            # decide qual seq vai enviar agora
            seq_to_send = i
            if (i == 1) and (not erro_injetado) and (i + 1 < total):
                seq_to_send = i + 1  # manda o 2 antes do 1
                erro_injetado = True


            # monta o pacote conforme seq_to_send (não o i!)
            start = seq_to_send * p.MAX_PAY
            end   = start + p.MAX_PAY
            payload = data[start:end]
            pacote  = p.cria_pacote(seq_to_send, total, payload)
            crc     = p.calcula_crc16(payload)

            # envia
            com.sendData(np.asarray(pacote))
            escreve("client_log.txt", "envio", len(payload), seq_to_send, total, crc)
            print(f"[CLI] Pacote {seq_to_send+1}/{total} enviado")

            # aguarda 1 byte: ACK(0x01) ou NAK(0x00)
            rx, _ = com.getData(1)

            if rx == b"\x01":  # ACK
                if seq_to_send == i:
                    print(f"[CLI] ACK recebido ({i+1}/{total})")
                    escreve("client_log.txt", "receb", 0, i, total, crc)
                    i += 1
                else:
                    # Teoricamente não deve acontecer (server não aceita fora de ordem)
                    print(f"[CLI] ACK inesperado para seq {seq_to_send} (server aceitou fora de ordem?)")

            else:  # NAK
                if seq_to_send != i:
                    print(f"[CLI] Server reclamou do pacote fora de ordem (mandei {seq_to_send}, esperava {i}).")
                    print(f"[CLI] Reenviando o pacote correto seq {i} e só continuo quando ACK chegar...")
                else:
                    print(f"[CLI] NAK para seq {i} (possível erro de CRC). Reenviando...")

                # Reenvia até ACK do pacote CORRETO (seq == i)
                while True:
                    start = i * p.MAX_PAY
                    end   = start + p.MAX_PAY
                    payload = data[start:end]
                    pacote  = p.cria_pacote(i, total, payload)
                    crc     = p.calcula_crc16(payload)

                    com.sendData(np.asarray(pacote))
                    escreve("client_log.txt", "envio", len(payload), i, total, crc)
                    print(f"[CLI] Reenviei seq {i+1}/{total}, aguardando ACK...")

                    rx2, _ = com.getData(1)
                    if rx2 == b"\x01":
                        print(f"[CLI] ACK do seq {i+1} recebido. Agora posso continuar.")
                        escreve("client_log.txt", "receb", 0, i, total, crc)
                        i += 1
                        break
                    else:
                        print(f"[CLI] NAK novamente no seq {i+1}. Tentando de novo...")

        print("[CLI] Transmissão concluída!")

    finally:
        com.disable()
        print("[CLI] fim")

if __name__ == "__main__":
    main()
