import os
import time as t
import numpy as np
import keyboard
from enlace import *
from pacote import Pacote
from txtgen import escreve

class Client():
    def __init__(self):
        self.COM = 'COM15'
        self.LOG = 'client_log.txt'

def main():
    client = Client()
    p = Pacote()
    com = enlace(client.COM)

    print("### inicializando cliente ###")
    t.sleep(1)
    try:
        com.enable()
        com.sendData(b'00')
        t.sleep(0.1)

        com.sendData(np.asarray(p.cria_pacote(p.T_HELLO)))
        escreve(client.LOG, "envio", 0, 0, 0, 0)

        tip, f, seq, total, payload = p.recebe_pacote(com, timeout=8)
        if tip != p.T_LIST:
            raise RuntimeError("esperava lista")
        escreve(client.LOG, "receb", len(payload), 0, 1, p.calcula_crc16(payload))

        nomes = payload.decode().strip().split('\n')
        print("arquivos disponíveis:")
        for i, nome in enumerate(nomes):
            print(i, nome)

        escolhas = [nomes[0]] if nomes else []
        file_state = {}
        for i, nome in enumerate(escolhas, start=1):
            get_pkg = p.cria_pacote(p.T_GET, file_id=i, payload=nome.encode())
            com.sendData(np.asarray(get_pkg))
            escreve(client.LOG, "envio", len(nome), 0, 1, p.calcula_crc16(nome.encode()))
            t2, f2, _, _, _ = p.recebe_pacote(com, timeout=5)
            if t2 != p.T_OK:
                raise RuntimeError("esperava OK")
            file_state[i] = {"nome": nome, "dados": bytearray(), "total": None, "esperado": 0}

        concluido = set()
        while len(concluido) < len(file_state):
            tip, f, s, tot, pl = p.recebe_pacote(com, timeout=15)
            if tip == p.T_DATA:
                escreve(client.LOG, "receb", len(pl), s, tot, p.calcula_crc16(pl))
                info = file_state[f]
                if s == info["esperado"]:
                    info["dados"].extend(pl)
                    info["esperado"] += 1
                    com.sendData(np.asarray(p.cria_pacote(p.T_ACK, file_id=f, seq=s)))
                    escreve(client.LOG, "envio", 0, s, tot, 0)
                else:
                    # retransmissão
                    com.sendData(np.asarray(p.cria_pacote(p.T_ACK, file_id=f, seq=info["esperado"]-1)))
            elif tip == p.T_END:
                out = f"recv_{f}_{os.path.basename(file_state[f]['nome'])}"
                with open(out, "wb") as fp:
                    fp.write(bytes(file_state[f]["dados"]))
                concluido.add(f)
            elif tip == p.T_ERRCRC:
                # pede reenvio
                com.sendData(np.asarray(p.cria_pacote(p.T_ACK, file_id=f, seq=file_state[f]["esperado"]-1)))

        print("todos os arquivos recebidos!")

    finally:
        com.disable()
        print("fim cliente")

if __name__ == '__main__':
    main()
