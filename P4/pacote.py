import os
imagem = 'new.png'
import crcmod

class Pacote():
    def __init__(self):
        self.head = b''
        self.payload = b''
        self.eop = b''
    
    def num_pacotes(self, img):
        image_size = os.path.getsize(img)
        if image_size > 50:
            if (image_size % 50) != 0:
                self.size = (image_size // 50) + 1
            else:
                self.size = (image_size // 50)
        else: 
            self.size = 1

        
        return self.size

    def num_bytes_pacotes(self, img):
        dic = {} # indice do pacote : num)bytes 
        image_size = os.path.getsize(img)
        qts_vezes_50_int = image_size // 50
        contador = 0
        while image_size > 50:
                dic[contador] = 50
                image_size = image_size - 50
                contador +=1
                if contador == qts_vezes_50_int:
                    dic[contador] = image_size                   
        return dic


    def gera_payloads(self, img):
        with open(img, 'rb') as f:
            image_data = f.read()

        payloads = []
        num_pacotes = self.num_pacotes(img)
        bytes_por_pacote = self.num_bytes_pacotes(img)

        start = 0
        for i in range(num_pacotes):
            tamanho_pacote = bytes_por_pacote[i]
            pacote = image_data[start:start + tamanho_pacote]
            payloads.append(pacote)
            start += tamanho_pacote

        return payloads
    def gera_heads(self, img):
        num_pacotes = self.num_pacotes(img)
        bytes_por_pacote = self.num_bytes_pacotes(img)
        heads = []
        
        for i in range(num_pacotes):
            #criando o head

            #h_0 = Quantos pacotes serão enviados?
            h_0 = self.size.to_bytes(1, byteorder = 'big')
            #h_1 = Número do pacote
            h_1 = i.to_bytes(1, byteorder = 'big')
            #h_2 = Tamanho do dado que o pacote pode transmitir
            j = bytes_por_pacote[i]
            h_2 = int(j).to_bytes(1, byteorder = 'big')
            #h_3 - Tipo do pacote (O - enviou, 1 - se recebi como 1 - confirmação, se recebi como 0 - reenvio))
            h_3 = int(0).to_bytes(1, byteorder = 'big')
            
            head = h_0 + h_1 + h_2 + h_3 + bytearray(6)

            heads.append(head)

        return heads
    
    def gera_eops(self, img):
        num_pacotes = self.num_pacotes(img)
        bytes_por_pacote = self.num_bytes_pacotes(img)
        eops = []
        
        for i in range(num_pacotes):
            #criando o head

            #eop_0
            eop_0 = (0).to_bytes(1, byteorder = 'big')
            #eop_1
            eop_1 = (0).to_bytes(1, byteorder = 'big')
            #eop_2
            eop_2 = (0).to_bytes(1, byteorder = 'big')
            
            eop = eop_0 + eop_1 + eop_2

            eops.append(eop)

        return eops
    
    def gera_crc16(self,payload):
        crc16_func = crcmod.mkCrcFun(0x11021, initCrc=0xFFFF, xorOut=0x0000)
        # Calcula o CRC-16
        crc_result = crc16_func(payload)
        #transformando em bytes
        crc_bytes = int(crc_result).to_bytes(2, byteorder = 'big')
        return crc_bytes
    
    def constroi_pacotes(self, img):
        head = self.gera_heads(img) 
        payload = self.gera_payloads(img)
        
        eop = self.gera_eops(img)
        pacotes = []
        for valor_head, valor_payload , valor_eop in zip(head,payload,eop):
            #crc16
            crc16_2bytes = self.gera_crc16(valor_payload)
            crf_fake = (0).to_bytes(2, byteorder = 'big')
            pacote = valor_head + crc16_2bytes +  valor_payload + valor_eop
            pacotes.append(pacote)
            
        
        return pacotes


            


        

            

        