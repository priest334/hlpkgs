from Crypto.Cipher import AES


def pkcs_padding(src, size):
    count = size - len(src)%size
    if count == size:
        return src
    return src + chr(count)*count

def pkcs_unpadding(src, size):
    if src[-1] > size:
        return src
    return src[0:-ord(chr(src[-1]))]

def zero_padding(src, size):
    count = size - len(src)%size
    if count == size:
        return src
    return src + chr(0)*count

def zero_unpadding(src, size):
    return src.rstrip('\x00')


def aes_encrypt(src, key):
    cipher = AES.new(zero_padding(key, AES.block_size).encode(), AES.MODE_ECB)
    data = cipher.encrypt(pkcs_padding(src, AES.block_size).encode())
    return bytearray(data).hex()

def aes_decrypt(src, key):
    bsrc = bytes.fromhex(src)
    cipher = AES.new(zero_padding(key, AES.block_size).encode(), AES.MODE_ECB)
    data = cipher.decrypt(bsrc)
    return pkcs_unpadding(data, AES.block_size).decode()


__all__ = ['aes_encrypt', 'aes_decrypt']
