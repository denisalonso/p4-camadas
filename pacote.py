import struct
import time as t
from enlace import *
import crc16


class Pacote(object):
    def __init__(self):
        # protocolo
        self.EOP = b'\xAA\xBB\xCC\xDD'  # 4 bytes - 10101010 10111011 11001100 11011101
        self.HDR_LEN = 10               # tamanho do head - 12 bytes
        self.MAX_PAY = 100              # payload maximo por pacote
        
        # tipos de msg
        self.T_HELLO = 1
        self.T_LIST  = 2
        self.T_GET   = 3
        self.T_OK    = 4
        self.T_DATA  = 5
        self.T_ACK   = 6
        self.T_END   = 7
        self.T_ABORT = 8
    
    def checksum16(self, payload):  #retorna um numero inteiro representavel em 32 bits (max: 2^32 - 1)
        return crc16.crc16xmodem(payload) & 0xFFFF
    
    def cria_header(self, tipo, file_id, seq, total, plen, crc): # header de 12 bytes
        return struct.pack(">BBHHHH",           # formato de dados > = MSB da esquerda pra direita 
                           tipo & 0xFF,         # B -> char 1 byte
                           file_id & 0xFF,      # B -> char 1 byte
                           seq & 0xFFFF,        # H -> short 2 bytes
                           total & 0xFFFF,      # H -> short 2 bytes
                           plen & 0xFFFF,       # H -> short 2 bytes
                           crc & 0xFFFF         # H -> short 2 bytes
                           )

    def int_header(self, head): # interpreta o header
        tipo, fid, seq, total, plen, crc = struct.unpack('>BBHHHH',head)
        return tipo, fid, seq, total, plen, crc

    def cria_pacote(self, tipo, file_id=0, seq=0, total=0, payload=b''):
        plen = len(payload)
        if plen > self.MAX_PAY:
            raise ValueError('payload maior que MAX_PAY')
        head = self.cria_header(tipo,file_id,seq,total,plen,self.checksum16(payload))
        return head + payload + self.EOP
    
    def recebe_pacote(self, com, timeout=5.0):
        t0 = t.time()
        buf = b''
        while (t.time() - t0) < timeout:
            if com.rx.getBufferLen() > 0:
                pedaco = com.rx.getAllBuffer(0)
                buf += pedaco
                i = buf.find(self.EOP)
                if i >= 0:
                    pac = buf[:i]                               # head + payload
                    resto = buf[i + len(self.EOP):]
                    # devolve sobra ao buffer rx
                    com.rx.threadPause()
                    com.rx.buffer = resto + com.rx.buffer
                    com.rx.threadResume()
                    if len(pac) < self.HDR_LEN:
                        raise ValueError('pacote sem header')
                    hdr = pac[:self.HDR_LEN]
                    payload = pac[self.HDR_LEN:]
                    tipo, fid, seq, total, plen, crc = self.int_header(hdr)
                    if plen != len(payload):
                        raise ValueError('plen inconsistente')
                    if self.checksum16(payload) != crc:
                        raise ValueError('checksum invalido')
                    return tipo, fid, seq, total, payload
            t.sleep(0.1)
        raise TimeoutError('timeout - recebe_pacote')

    def divide(self, data): # divide um grande número de bytes em pedacos menores de tamanho self.MAX_PAY
        if len(data) == 0:
            return [b'']
        else:
            pacs = []
            for i in range(0,len(data),self.MAX_PAY):
                pacs.append(data[i:i+self.MAX_PAY])
        return pacs

    def arquivo_pra_pacote(self,file_id,data):
        pedacos = self.divide(data)
        total = len(pedacos)
        pacs = []
        for seq, payload in enumerate(pedacos):
            pacs.append(self.cria_pacote(self.T_DATA, file_id=file_id, seq=seq, total=total, payload=payload))
        return pacs, total