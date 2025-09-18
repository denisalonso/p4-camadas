
        
import os
import crcmod
class Interpretador():
    def __init__(self,pacote_entrada):
        # HEAD
        self.head = list(pacote_entrada)[:12]
        self.size_all_packages = self.head[0]
        self.package_number = self.head[1]
        self.payload_size = self.head[2]
        self.conf_byte = self.head[3]
        self.crc16 = self.head[-2:]
        
        
    def get_eop(nx,pacote_entrada):
        return list(pacote_entrada)[0]

    def gera_crc16(self,payload):
        crc16_func = crcmod.mkCrcFun(0x11021, initCrc=0xFFFF, xorOut=0x0000)
        # Calcula o CRC-16
        crc_result = crc16_func(payload)
        #transformando em bytes
        crc_bytes = int(crc_result).to_bytes(2, byteorder = 'big')
        return crc_bytes
    
    def check_crc16(self,crc_bytes):
        if bytes(self.crc16) == crc_bytes:
            return True
        else:
            return False
        
        

        