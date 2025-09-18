#####################################################
# Camada Física da Computação
#Carareto
#11/08/2022
#Aplicação
####################################################


#rode o comando pip install -r requirements.txt
from recepcao import Interpretador
from requester import escreve

from enlace import *
import time
import numpy as np
import os
from pacote import Pacote
import threading

import crcmod

serialName = "COM8"                  # Windows(variacao de)

class TimeoutError(Exception):
    pass

def timeout_mensagem(com1):
    print("Servidor inativo. Tentar novamente? S/N")
    answer = input()
    if answer == "S":
        h_0 = int(1).to_bytes(1, byteorder = 'big')
        h_1 = int(1).to_bytes(1, byteorder = 'big')
        h_2 = int(1).to_bytes(1, byteorder = 'big')
        h_3 = int(1).to_bytes(1, byteorder = 'big')
        handshake = h_0 + h_1 + h_2 + bytearray(9) + h_3 +bytearray(3)
        print('HANDSHAKEEEEEEE', handshake)   
        while com1.rx.getBufferLen() ==0:
            time.sleep(1)
            com1.sendData(np.asarray(handshake))
            print('Reenviando HandShake')


    else:
        raise TimeoutError("Transmissão interrompida")

def main():
    try:
        print("Iniciou o main")
        #declaramos um objeto do tipo enlace com o nome "com". Essa é a camada inferior à aplicação. Observe que um parametro
        #para declarar esse objeto é o nome da porta.
        com1 = enlace(serialName)
        com1.enable()
        time.sleep(.2)
        imagem = 'img/image.png'
        print("Abriu a comunicação")
        print("enviando 1 byte de sacrifício")

        com1.sendData(b'00')
        
        time.sleep(1)
        #txBuffer = imagem em bytes
        p = Pacote()
        #HANDSHAKEEEEEEEEEEEEEEEEEEEEEEEEE
        h_0 = int(1).to_bytes(1, byteorder = 'big')
        h_1 = int(1).to_bytes(1, byteorder = 'big')
        h_2 = int(1).to_bytes(1, byteorder = 'big')
        h_3 = int(1).to_bytes(1, byteorder = 'big')
        handshake = h_0 + h_1 + h_2 + bytearray(9) + h_3 +bytearray(3)
        print('HANDSHAKEEEEEEE', handshake)   
        
        com1.sendData(np.asarray(handshake))
        print('HandShake enviado')
        
        # Definindo o timeout de 5 segundos
        timeout = 5
        timer = threading.Timer(timeout, timeout_mensagem,args=[com1])
        timer.start()

        
        print("esperando resposta do handshake")
        rxBuffer, nRx = com1.getData(12)
        print(rxBuffer,' recebendo Confirmação')

        # Cancelar o timer se os dados forem recebidos dentro do tempo limite
        timer.cancel()

        

        entrada = Interpretador(rxBuffer)
        payload_confirm, nRx = com1.getData(entrada.payload_size)
        print(payload_confirm)
        com1.rx.clearBuffer()

        if payload_confirm == int.to_bytes(1,length=1, byteorder = 'big'):
            print('Confirmado')
            ps = p.constroi_pacotes(imagem)
            ####################
            i=3
            while i < p.num_pacotes(imagem): 
                pacote_da_vez = ps[i]
                #envia pacote:
                com1.sendData(np.asarray(pacote_da_vez))
                print("esperando confirmação de recepção do pacote")

                rxBuffer, nRx = com1.getData(15)
                print(rxBuffer, '----------------------------')
                
                #checagem se h_3 é igual a 1 (se foi recebido)
                print("checagem se h_3 é igual a 1 ", rxBuffer[3])
                if rxBuffer[3] == 1:

                    ok = rxBuffer[4]
                    print("indice pedido", ok, "----------------------------------------------------------")


                    lista_pacote = list(pacote_da_vez)
                    tamanho_pacote = len(lista_pacote)
                    num_pacote = lista_pacote[1]
                    all_pacotes = lista_pacote[0]
                    # Calcula o CRC-16
                    crc_bytes = pacote_da_vez[10:12]
                    #transformando em bytes
                    mensagem = escreve("requests_client.txt","envio",tamanho_pacote,num_pacote,all_pacotes,crc_bytes)
                    print(mensagem)
                    print(rxBuffer,'pacote enviado pelo client')
                    #autorizado a enviar o próximo pacote
                    i+=1
                else:
                    #pedir o índice certo do pacote

                    print(list(rxBuffer))
                    i = rxBuffer[4]
    
                    print("voltou para o índice", i, "----------------------------------------------------------")


        com1.disable()
        
    except Exception as erro:
        print("ops! :-\\")
        print(erro)
        com1.disable()
        

    #so roda o main quando for executado do terminal ... se for chamado dentro de outro modulo nao roda
if __name__ == "__main__":
    main()
