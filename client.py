import time as t
from enlace import *
from pacote import Pacote


class Client(object):
    def __init__(self):
        self.PORTA = 'COM'
        self.SAC = b'\xAF\xAF' # byte de sacrificio
        self.com = enlace(self.PORTA)
        self.com.enable()
        
    

def main():
    # inicialização de objetos
    c = Client()
    p = Pacote()

    # inicializacao
    print('#################################################')
    print('#####        Servidor inicializando         #####') 
    print('#################################################')
    t.sleep(1)
    print('Estabelecendo comunicação com o servidor...')
    # criacao do pacote vazio com mensagem HELLO
    hello = p.cria_pacote(p.cria_header(p.HELLO,0,0,1,1,p.calcula_crc16(c.SAC)),c.SAC,p.EOP)
    c.com.sendData(hello)
    t.sleep(1)
    print('Enviando o byte de sacrifício...')
    


if __name__ == '__main__':
    main()