import struct
import time as t
from enlace import *
import crcmod

class Pacote(object):
    def __init__(self):
        self.EOP = b'\xAA\xBB\xCC\xDD'  # delimitador
        self.HDR_LEN = 10               # 1+1+2+2+2+2 = 10 bytes
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
        self.T_ERRCRC = 9   # novo tipo de mensagem para CRC errado

    def checksum16(self, payload: bytes) -> int:
        """Calcula CRC16-XMODEM (2 bytes) do payload"""
        crc16 = crcmod.predefined.Crc('xmodem')
        crc16.update(payload)
        return crc16.crcValue & 0xFFFF

    def cria_header(self, tipo, file_id, seq, total, plen, crc):
        return struct.pack(">BBHHHH",
                           tipo & 0xFF,
                           file_id & 0xFF,
                           seq & 0xFFFF,
                           total & 0xFFFF,
                           plen & 0xFFFF,
                           crc & 0xFFFF)

    def int_header(self, head):
        tipo, fid, seq, total, plen, crc = struct.unpack(">BBHHHH", head)
        return tipo, fid, seq, total, plen, crc

    def cria_pacote(self, tipo, file_id=0, seq=0, total=0, payload=b''):
        plen = len(payload)
        if plen > self.MAX_PAY:
            raise ValueError('payload maior que MAX_PAY')
        crc = self.calcula_crc16(payload)
        head = self.cria_header(tipo, file_id, seq, total, plen, crc)
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
                    pac = buf[:i]
                    resto = buf[i + len(self.EOP):]
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
                    if self.calcula_crc16(payload) != crc:
                        # retorno com tipo especial para server poder avisar
                        return self.T_ERRCRC, fid, seq, total, payload
                    return tipo, fid, seq, total, payload
            t.sleep(0.1)
        raise TimeoutError('timeout - recebe_pacote')

    def divide(self, data):
        if len(data) == 0:
            return [b'']
        return [data[i:i+self.MAX_PAY] for i in range(0, len(data), self.MAX_PAY)]

    def arquivo_pra_pacote(self, file_id, data):
        pedacos = self.divide(data)
        total = len(pedacos)
        pacs = []
        for seq, payload in enumerate(pedacos):
            pacs.append(self.cria_pacote(self.T_DATA, file_id=file_id, seq=seq, total=total, payload=payload))
        return pacs, total
