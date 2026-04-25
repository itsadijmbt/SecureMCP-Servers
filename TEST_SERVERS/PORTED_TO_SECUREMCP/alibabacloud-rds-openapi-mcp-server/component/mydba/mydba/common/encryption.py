# -*- coding: utf-8 -*-
import os
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

def encrypt(key: str, plain_data: str) -> str:
    """
    AES-CBC 加密
    Args:
        key (str): 16/24/32 字节的密钥（对应 AES-128/AES-192/AES-256）
        plain_data (str): 明文文本
    Returns:
        str: iv + 密文
    """
    if not plain_data:
        return plain_data
    key = key.encode('utf-8')
    plain_data = plain_data.encode('utf-8')
    # 生成随机 16 字节 IV
    iv = os.urandom(16)
    # 添加 PKCS7 填充
    padder = padding.PKCS7(128).padder()
    padded_data = padder.update(plain_data) + padder.finalize()
    # 创建加密器
    cipher = Cipher(
        algorithms.AES(key),
        modes.CBC(iv),
        backend=default_backend()
    )
    encryptor = cipher.encryptor()
    # 加密并返回 iv + 密文
    ciphertext = encryptor.update(padded_data) + encryptor.finalize()
    return (iv + ciphertext).hex()

def decrypt(key: str, cipher_data: str) -> str:
    """
    AES-CBC 解密
    Args:
        key (str): 与加密时相同的密钥
        cipher_data (str): iv + 密文
    Returns:
        str: 解密后的明文
    """
    if not cipher_data:
        return cipher_data
    key = key.encode('utf-8')
    cipher_data = bytes.fromhex(cipher_data)
    # 提取 IV 和密文
    iv = cipher_data[:16]
    cipher_data = cipher_data[16:]
    # 创建解密器
    cipher = Cipher(
        algorithms.AES(key),
        modes.CBC(iv),
        backend=default_backend()
    )
    decryptor = cipher.decryptor()
    # 解密并去除填充
    padded_plaintext = decryptor.update(cipher_data) + decryptor.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
    return plaintext.decode('utf-8')
