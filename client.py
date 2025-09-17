import os
import time as t
import numpy as np
from enlace import *
from pacote import Pacote
import keyboard

class Client():
    def __init__(self):
        self.COM = 'COM15' # insira sua porta COM aqui

# oi
def main():
    client = Client()
    p = Pacote()

    com = enlace(client.COM)
    print('#####################################################')
    print('######       inicializando o --CLIENTE--      #######')
    print('#####################################################')
    time.sleep(1)
    try:
        com.enable()
        print(f'porta aberta: {client.COM}')
        t.sleep(1)
        
        # byte de sacrificio
        com.sendData(b'00')
        t.sleep(1)

        # hello
        com.sendData(np.asanyarray(p.cria_pacote(p.T_HELLO)))
        print('hello enviado')

        # recebe lista (payload = nomes separados por '\n')
        tip, f, seq, total, payload = p.recebe_pacote(com,timeout=8)
        if tip != p.T_LIST:
            raise RuntimeError('esperava a lista de arquivos do servidor')
        if payload:
            nomes = payload.decode('utf-8').strip().split('\n')
        else:
            nomes = []
        print('arquivos disponíveis: ')
        
        for nome in nomes:
            print(f"{nome}: {nomes.index(nome)}")

        t.sleep(1)

        escolhas = []
        while True:
            arq = input('digite o indice do arquivo que voce quer (digite "q" pra sair): ')
            if arq == 'q':
                break
            else:
                try:
                    escolhas.append(nomes[int(arq)])
                except:
                    print('indice nao consta na lista de arquivos!')

        # escolhe 2 (ou menos se só houver 1)
        # escolhas = nomes[] if len(nomes) >= 2 else nomes
        if not escolhas:
            raise RuntimeError("Servidor não forneceu arquivos")
    
        # envia get para cada escolha
        file_state = {}  # f -> {nome, dados(bytearray), total:int|None, esperado:int}
        for i, nome in enumerate(escolhas, start=1):
            com.sendData(np.asarray(p.cria_pacote(p.T_GET, file_id=i, payload=nome.encode("utf-8"))))
            print(f"get: f={i} nome='{nome}'")
            # espera OK correspondente
            t2, f2, _, _, _ = p.recebe_pacote(com, timeout=5)
            if t2 != p.T_OK or f2 != i:
                raise RuntimeError("esperava ok do get mas veio outro tipo")
            file_state[i] = {"nome": nome, "dados": bytearray(), "total": None, "esperado": 0}
        t.sleep(1)
        print("iniciando recepção intercalada (ACK por pacote)...")
        concluido = set()

        pausado = False
        abortado = False
        while len(concluido) < len(file_state):
            
            if keyboard.is_pressed('p'):
                pausado = not pausado
                print('pausado' if pausado else 'retomando')
                t.sleep(0.5)
            
            if keyboard.is_pressed('x'):
                abortado = True
                print('transferencia abortada!')
                com.sendData(np.asarray(p.cria_pacote(p.T_ABORT)))
                break

            if not pausado:
                try:
                    tip, f, s, tot, pl = p.recebe_pacote(com, timeout=15)
                except TimeoutError:
                    print("timeout esperando")
                    continue

                if tip == p.T_DATA:
                    info = file_state.get(f)
                    if not info or f in concluido:
                        # ACK do último válido para evitar travar do outro lado
                        last_ok = (info["esperado"] - 1) if info else 0
                        com.sendData(np.asarray(p.cria_pacote(p.T_ACK, file_id=f, seq=max(0, last_ok))))
                        continue

                    if info["total"] is None and tot != 0:
                        info["total"] = tot

                    if s == info["esperado"]:
                        info["dados"].extend(pl)
                        info["esperado"] += 1
                        com.sendData(np.asarray(p.cria_pacote(p.T_ACK, file_id=f, seq=s)))
                        if info["total"] is not None:
                            print(f"{info['nome']}  {s+1}/{info['total']}")
                    else:
                        # re-ACK do último correto para acionar retransmissão
                        com.sendData(np.asarray(p.cria_pacote(p.T_ACK, file_id=f, seq=max(0, info["esperado"]-1))))

                    # terminou esse arquivo?
                    if info["total"] is not None and info["esperado"] >= info["total"]:
                        out = f"recv_{f}_{os.path.basename(info['nome'])}"
                        with open(out, "wb") as fp:
                            fp.write(bytes(info["dados"]))
                        print(f"[CLI] Salvo: {out}  ({len(info['dados'])} bytes)")
                        com.sendData(np.asarray(p.cria_pacote(p.T_END, file_id=f)))
                        concluido.add(f)

                elif tip == p.T_END:
                    # opcional: ACK final
                    com.sendData(np.asarray(p.cria_pacote(p.T_ACK, file_id=f, seq=0)))
                else:
                    # ignora outros tipos aqui
                    pass
        if not abortado:
            print("todos os arquivos recebidos com sucesso!")

    finally:
        com.disable()
        print('fim do projeto')

if __name__ == '__main__':
    main()