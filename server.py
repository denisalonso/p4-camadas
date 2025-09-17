import os
import time as t
import numpy as np
from enlace import *
from pacote import Pacote

class Server():
    def __init__(self):
        self.COM = 'COM14'      # insira sua porta com aqui
        self.DIR = './files'    # pasta que sera lida

    def load_files(self):
        files = []
        if os.path.isdir(self.DIR):
            for file in os.listdir(self.DIR):
                p = os.path.join(self.DIR,file)
                if os.path.isfile(p):
                    files.append(p)
        return files
    
def main():
    server = Server()
    com = enlace(server.COM)
    p = Pacote()
    print('#####################################################')
    print('#######      inicializando o --SERVIDOR--     #######')
    print('#####################################################')
    t.sleep(1)
    try:
        com.enable()
        print(f'\porta aberta: {server.COM}!')
        t.sleep(1)
        
        # byte de sacrificio
        print('esperando o byte de sacrifício...')
        rx, _ = com.getData(1)
        com.rx.clearBuffer()
        t.sleep(.1)

        # esperar HELLO
        tip, f, s, tot, pl = p.recebe_pacote(com, timeout=15.0)
        if tip != p.T_HELLO:
            raise RuntimeError('o cliente nao disse oi. grosso')
        print('mensagem HELLO recebida!')

        # envia lista de arquivos
        nomes = server.load_files()
        lista = '\n'.join(nomes).encode('utf-8')
        com.sendData(np.asarray(p.cria_pacote(p.T_LIST,payload=lista)))
        print(f'lista de {len(nomes)} arquivos enviada')

        # recebe T_GETs espera 2 mas aceita 3
        arquivos = {}
        while True:
            try:
                tip, f, s, tot, pl = p.recebe_pacote(com,timeout=15.0)
            except TimeoutError:
                break
            if tip == p.T_GET:
                nome = pl.decode('utf-8')
                if not os.path.isfile(nome):
                    # se não existir, responde OK mesmo assim (ou crie um erro específico)
                    com.sendData(np.asarray(p.cria_pacote(p.T_OK, file_id=f)))
                    print(f"GET '{nome}' (f={f}) - arquivo não encontrado; enviando OK mesmo")
                    continue
                with open(nome, "rb") as fp:
                    data = fp.read()
                pacs, total_pacs = p.arquivo_pra_pacote(f, data)
                arquivos[f] = {
                    "nome": nome,
                    "data": data,
                    "pacs": pacs,
                    "total": total_pacs,
                    "next_seq": 0
                }
                com.sendData(np.asarray(p.cria_pacote(p.T_OK, file_id=f)))
                print(f"GET ok: f={f}, '{nome}', {total_pacs} pacotes")
            else:
                # qualquer outro tipo encerra a fase de GET
                break
        if not arquivos:
            print("nenhum arquivo selecionado; encerrando")
            return
        
        print("iniciando transmissão alternada…")
        ativos = set(arquivos.keys())
        ordem = sorted(list(ativos))
        ACK_TIMEOUT = 2.0

        abortado = False
        
        while ativos:
            for f in list(ordem):
                if f not in ativos:
                    continue
                info = arquivos[f]
                seq = info["next_seq"]

                if seq >= info["total"]:
                    # já acabou: envia END uma vez
                    com.sendData(np.asarray(p.cria_pacote(p.T_END, file_id=f)))
                    print(f"END enviado (f={f})")
                    ativos.remove(f)
                    continue

                # envia DATA (um pacote por rodada, intercalando arquivos)
                pac = info["pacs"][seq]
                com.sendData(np.asarray(pac))

                # espera ACK do mesmo seq
                t0 = t.time()
                ack_ok = False
                while (t.time() - t0) < ACK_TIMEOUT:
                    try:
                        t2, f2, s2, tot2, pl2 = p.recebe_pacote(com, timeout=ACK_TIMEOUT)
                        if t2 == p.T_ACK and f2 == f and s2 == seq:
                            ack_ok = True
                            break
                        elif t2 == p.T_ABORT:
                            abortado = True
                            print('transferencia abortada pelo cliente')
                            break
                        else:
                            continue

                    except TimeoutError:
                        break
                if abortado:
                    break
                if ack_ok:
                    info["next_seq"] += 1
                    print(f"ACK ok  f={f}  {seq+1}/{info['total']}")
                else:
                    print(f"ACK timeout -> retransmitir f={f} seq={seq}")
                    # não incrementa; no próximo round envia o mesmo seq
            if abortado:
                    break
            
        if not abortado:
            print("todos os arquivos enviados!")

    
    finally:
        com.disable()
        print('fim do projeto')

if __name__ == '__main__':
    main()