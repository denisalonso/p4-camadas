import struct
from enlace import *
import time
import numpy as np
from recepcao import Interpretador
from requester import escreve
serialName = "COM8"  # Altere conforme necessário
def confirmacao():
    h_0 = int(1).to_bytes(1, byteorder = 'big')
    h_1 = int(1).to_bytes(1, byteorder = 'big')
    h_2 = int(1).to_bytes(1, byteorder = 'big')
    h_3 = int(1).to_bytes(1, byteorder = 'big')

    conf = h_0 + h_1 + h_2 + h_3+ bytearray(8) + bytearray(3)
    print('Confirmado', conf)
    print("Enviando resposta de Confirmação")
    return conf

def negado():
    h_0 = int(1).to_bytes(1, byteorder = 'big')
    h_1 = int(1).to_bytes(1, byteorder = 'big')
    h_2 = int(1).to_bytes(1, byteorder = 'big')
    h_3 = int(0).to_bytes(1, byteorder = 'big')

    neg = h_0 + h_1 + h_2 + h_3+ bytearray(8) + bytearray(3)
    print('Negado', neg)
    print("Enviando pedido de reenvio")
    return neg
def main():
    try:
        print("Iniciou o main")
        print("Abriu a comunicação")
        
        com1 = enlace(serialName)
        com1.enable()
        
        #Lista de pacotes recebidos
        lista_de_pacotes = []
        
        
        print("esperando 1 byte de sacrifício")
        rxBuffer, nRx = com1.getData(1)
        com1.rx.clearBuffer()
        time.sleep(.1)
        
        
        #HandShake checagem
        rxBuffer, nRx = com1.getData(12)
        entrada = Interpretador(rxBuffer)
        payload_confirm, nRx = com1.getData(entrada.payload_size)
        com1.rx.clearBuffer()
        
        if payload_confirm == int.to_bytes(1,length=1, byteorder = 'big'):
            #HANDSHAKEEEEEEEEEEEEEEEEEEEEEEEEE
            h_0 = int(1).to_bytes(1, byteorder = 'big')
            h_1 = int(1).to_bytes(1, byteorder = 'big')
            h_2 = int(1).to_bytes(1, byteorder = 'big')
            h_3 = int(1).to_bytes(1, byteorder = 'big')

            handshake = h_0 + h_1 + h_2 + bytearray(9) + h_3 +bytearray(3)
            print('HANDSHAKEEEEEEE', handshake)
            print("Enviando resposta de Confirmação ao HANDSHAKEEEEEEE")
            com1.sendData(np.asarray(handshake))
            
        
        

        rxBuffer, nRx = com1.getData(12)
        print('recebendo primeiro pacote', rxBuffer)
        entrada = Interpretador(rxBuffer)
        print(entrada.head, "entrada")
        payload,nRx = com1.getData(entrada.payload_size)
        print(payload, "entrada")
        eop = entrada.get_eop(com1.getData(3))
        print(eop,'eopppp')
        if eop == b'\x00\x00\x00':
            lista_de_pacotes.append(payload)
            con = confirmacao()
            com1.sendData(np.asarray(con))
        print(lista_de_pacotes,'primeiro pacote recebido')

        i = entrada.package_number + 1
        total = entrada.size_all_packages
        num_pacote_prox = entrada.package_number +1
        

        while i < total:
            rxBuffer, nRx = com1.getData(12)
            print(f'recebendo {i} pacote')
            entrada = Interpretador(rxBuffer)
            payload,nRx = com1.getData(entrada.payload_size)
            crc_bytes = entrada.gera_crc16(payload)
            confirmacao_crc = entrada.check_crc16(crc_bytes)
            eop = entrada.get_eop(com1.getData(3))
            print(eop,'eopppp')
            print(entrada.package_number ,"numero do pacote")
            if eop == b'\x00\x00\x00':
                
                if entrada.package_number == num_pacote_prox:
                    print(num_pacote_prox ,'BBBBBBBBBBBBBBBBB')
                    num_pacote_prox = entrada.package_number +1
                    if confirmacao_crc:
                        print('CONFIRMADO CRC')
                        lista_de_pacotes.append(payload)
                        i += 1
                        con = confirmacao()
                        com1.sendData(np.asarray(con))
                        tamanho_pacote = len(entrada.head) + len(payload) + len(eop)
                        mensagem = escreve("requests_server.txt","recebimento",tamanho_pacote,entrada.package_number,entrada.size_all_packages,crc_bytes)
                        print(mensagem)
                        
                    else:
                        print(crc_bytes,"AAAAAAAAAAAAAAAA",entrada.crc16)
                        print('NEGADO CRC')

                        con = negado()
                        com1.sendData(np.asarray(con))
                    
    
        print(len(lista_de_pacotes))
        
        with open('imagem_recebido.png','wb') as file:
            for pacote in lista_de_pacotes:
                file.write(pacote)





        



        print("-------------------------")
        print("Comunicação encerrada")
        print("-------------------------")
        com1.disable()

    except TimeoutError as e:
        print(e)
        com1.disable()
    except Exception as erro:
        print("ops! :-\\")
        print(erro)
        com1.disable()

if __name__ == "__main__":
    main()

