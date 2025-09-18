import struct

def float_to_bytes(num):
    bits, = struct.unpack('!I', struct.pack('!f', num))
    bits = "{:032b}".format(bits)
    print('total:', bits)
    print('IEEE-754','sign:', bits[0],'exponent:', bits[1:9],'mantissa:', bits[9:])

    bytes = int(bits, 2).to_bytes(4, byteorder='big')
    return bytes

ok = float_to_bytes(30.12)
print(ok)


def bytes_to_float(byte_data):
    # Desempacota diretamente os bytes para um número float
    float_num, = struct.unpack('!f', byte_data)
    return float_num