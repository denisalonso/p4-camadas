import time as t
from enlace import *
from pacote import Pacote


class Server(object):
    def __init__(self):
        self.PORTA = 'COM'
        self.com = enlace(self.PORTA)
        self.com.enable()

def main():
    # inicializacao de objetos
    s = Server()
    p = Pacote()

    # inicializacao
    print('#################################################')
    print('#####        Servidor inicializando         #####') 
    print('#################################################')
    t.sleep(1)
    print('Estabelecendo comunicação com o cliente...')
    t.sleep(1)
    print('Esperando o byte de sacrifício...')
    while s.com.rx.getBufferLen() == 0:
        pass
    msg_inicial = s.com.rx.getAllBuffer(s.com.rx.getBufferLen())
    print('Byte de sacrificio recebido!')
    

if __name__ == '__main__':
    main()