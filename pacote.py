# # pacote.py
# import struct
# import time as t
# import crcmod

# class Pacote:
#     def __init__(self):
#         self.EOP = b'\xAA\xBB\xCC\xDD'
#         self.HDR_LEN = 8   # seq(2) + total(2) + plen(2) + crc(2)
#         self.MAX_PAY = 100
        
#     def calcula_crc16(self, payload: bytes) -> int:
#         crc16 = crcmod.predefined.Crc('xmodem')
#         crc16.update(payload)
#         return crc16.crcValue & 0xFFFF

#     def cria_header(self, seq, total, plen, crc):
#         return struct.pack(">HHHH", seq, total, plen, crc)

#     def int_header(self, head):
#         return struct.unpack(">HHHH", head)

#     def cria_pacote(self, seq, total, payload: bytes):
#         plen = len(payload)
#         if plen > self.MAX_PAY:
#             raise ValueError("payload maior que o máximo permitido")
#         crc = self.calcula_crc16(payload)
#         head = self.cria_header(seq, total, plen, crc)
#         return head + payload + self.EOP

#     def recebe_pacote(self, com, timeout=5.0):
#         t0 = t.time()
#         buf = b""
#         while (t.time() - t0) < timeout:
#             if com.rx.getBufferLen() > 0:
#                 buf += com.rx.getAllBuffer(0)
#                 i = buf.find(self.EOP)
#                 if i >= 0:
#                     pac = buf[:i]
#                     resto = buf[i+len(self.EOP):]
#                     com.rx.threadPause()
#                     com.rx.buffer = resto + com.rx.buffer
#                     com.rx.threadResume()
#                     hdr = pac[:self.HDR_LEN]
#                     payload = pac[self.HDR_LEN:]
#                     seq, total, plen, crc = self.int_header(hdr)
#                     if plen != len(payload):
#                         raise ValueError("plen inconsistente")
#                     return seq, total, plen, crc, payload
#             t.sleep(0.1)
#         raise TimeoutError("timeout - recebe_pacote")
# pacote.py
import struct
import time as t
import crcmod.predefined  # <- garante o submódulo 'predefined'

class Pacote:
    def __init__(self):
        self.EOP = b'\xAA\xBB\xCC\xDD'
        self.HDR_LEN = 8   # seq(2) + total(2) + plen(2) + crc(2)
        self.MAX_PAY = 100
        # só por referência, mas aqui a gente usa ACK/NAK de 1 byte (0x01/0x00)
        self.T_ACK   = 6
        self.NACK    = 4

    def calcula_crc16(self, payload: bytes) -> int:
        crc16 = crcmod.predefined.Crc('xmodem')
        crc16.update(payload)
        return crc16.crcValue & 0xFFFF

    def cria_header(self, seq, total, plen, crc):
        return struct.pack(">HHHH", seq, total, plen, crc)

    def int_header(self, head):
        return struct.unpack(">HHHH", head)

    def cria_pacote(self, seq, total, payload: bytes):
        plen = len(payload)
        if plen > self.MAX_PAY:
            raise ValueError("payload maior que o máximo permitido")
        crc = self.calcula_crc16(payload)
        head = self.cria_header(seq, total, plen, crc)
        return head + payload + self.EOP

    def recebe_pacote(self, com, timeout=5.0):
        t0 = t.time()
        buf = b""
        while (t.time() - t0) < timeout:
            if com.rx.getBufferLen() > 0:
                buf += com.rx.getAllBuffer(0)
                i = buf.find(self.EOP)
                if i >= 0:
                    pac = buf[:i]
                    resto = buf[i+len(self.EOP):]
                    # devolve sobra para o buffer
                    com.rx.threadPause()
                    com.rx.buffer = resto + com.rx.buffer
                    com.rx.threadResume()
                    if len(pac) < self.HDR_LEN:
                        raise ValueError("pacote sem header")
                    hdr = pac[:self.HDR_LEN]
                    payload = pac[self.HDR_LEN:]
                    seq, total, plen, crc = self.int_header(hdr)
                    if plen != len(payload):
                        raise ValueError("plen inconsistente")
                    return seq, total, plen, crc, payload
            t.sleep(0.1)
        raise TimeoutError("timeout - recebe_pacote")
