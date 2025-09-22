import os
import crcmod

class Pacote(object):
    def __init__(self):
        self.hdr_len = 10
        self.MAX_PAYLOAD = 100
        self.EOP = b'\xAF\x8E\xFF\x02'

        self.HELLO =    1
        self.ACK =      2
        self.PAUSE =    3
        self.ABORT =    4
        self.FIN =      5

    def calcula_crc16(payload):
        crc16_func = crcmod.predefined.Crc('xmodem')
        crc16_func.update(payload)
        return crc16_func.crcValue & 0xFFFF
    
    def cria_header(self, tipo, id, seq, tpac, psize, crc):
        return bytes([tipo & 0xFF,
                      id & 0xFF,
                      (seq >> 8) & 0xFF, seq & 0xFF,
                      (tpac >> 8) & 0xFF, tpac & 0xFF,
                      (psize >> 8) & 0xFF, psize & 0xFF,
                      (crc >> 8) & 0xFF, crc & 0xFF
                      ])
    
    def int_header(self,pac):
        if len(pac) < self.hdr_len:
            raise ValueError('Pacote não tem Header!')
        header = pac[:self.hdr_len]
        tipo = header[0]
        id = header[1]
        seq = header[2]<<8|header[3]
        return 


    def cria_pacote(self,header,payload):
        return bytes([header, 
                      payload, 
                      self.EOP
                      ])
    
    def pay_list(self,caminho):
        with open(caminho, 'rb') as d:
            data = d.read()
        plds = []
        i = 0
        while i < len(data):
            if i + self.MAX_PAYLOAD >= len(data):
                payload = data[i:]
            else:
                payload = data[i:i+self.MAX_PAYLOAD]
            plds.append(payload)
            i += 100
        return bytes(plds)