#!/usr/bin/env python
# -*- coding: utf-8 -*-

import hashlib
import time

from Crypto.Cipher import DES, AES


_BS_ = 8
_pad_ = lambda s: s + (_BS_ - len(s) % _BS_) * chr(_BS_ - len(s) % _BS_)
_unpad_ = lambda s: s[0:-ord(s[-1])]

pad = lambda s, BS: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)


class Utils(object):

    @staticmethod
    def DES_decrypt(key, iv, data):
        cipher = DES.new(key, mode=DES.MODE_ECB, IV=iv)
        return _unpad_(cipher.decrypt(data))

    @staticmethod
    def DES_encrypt(key, iv, data):
        cipher = DES.new(key, mode=DES.MODE_ECB, IV=iv)
        return cipher.encrypt(pad(data, 8))

    @staticmethod
    def AES_decrypt(key, iv, data):
        if len(data) == 0:
            return ""
        cipher = AES.new(key, mode=AES.MODE_CBC, IV=iv)
        data = cipher.decrypt(data)

        return _unpad_(data)

    @staticmethod
    def AES_encrypt(key, iv, data):
        cipher = AES.new(key, mode=AES.MODE_CBC, IV=iv)
        return cipher.encrypt(pad(data, 16))

    @staticmethod
    def xor(data, key):
        return "".join(map(lambda c: chr(ord(c) ^ key), data))


class Account(object):
    def __init__(self, user_id, deviceToken):
        self.aes_key = hashlib.md5("ILovePerl").digest()
        self.userID = user_id
        self.DToken = deviceToken

    @property
    def cryptedUserID(self):
        if not hasattr(self, "_cryptUserID"):
            cryptUserID = Utils.DES_encrypt("5t216ObT", "5t216ObT", self.userID)
            self._cryptUserID = "".join(map(lambda c: "%02x" % ord(c), cryptUserID))
        return self._cryptUserID

    @property
    def hashedUserID(self):
        if not hasattr(self, "_hashedUserID"):
            self._hashedUserID = hashlib.sha1("TYhGo022TyofIxfs2gRVoUuyWwv0iR2G0FgAC9ml" + self.userID).hexdigest()
        return self._hashedUserID

    @property
    def requestIV(self):
        if not hasattr(self, "_requestIV"):
            self._requestIV = hashlib.md5(self.cryptedUserID).digest()
        return self._requestIV

    @property
    def requestKey(self):
        if not hasattr(self, "_requestKey"):
            self._requestKey = hashlib.md5("ILovePerl").digest()
        return self._requestKey

    @property
    def timestamp(self):
        stamp = int(time.time() - 28800)
        return self.encrypt("%smerctotostoria" % stamp)

    @property
    def deviceToken(self):
        if not hasattr(self, "_deviceToken"):
            deviceToken = Utils.DES_encrypt("00e2fdaa", "00e2fdaa", self.DToken)
            self._deviceToken = "".join(map(lambda c: "%02x" % ord(c), deviceToken))
        return self._deviceToken

    def encrypt(self, data):
        return Utils.AES_encrypt(self.requestKey, self.requestIV, data)

    def decrypt(self, data):
        return Utils.AES_decrypt(self.requestKey, self.requestIV, data)


class Auth(object):
    version = "\x00d"
    checksumKey = "%^&*@Q0je35i7qp9"

    def __init__(self):
        self.response_key = 113
        self.request_key = 195

    def encode(self, data, key):
        return "".join(map(lambda c: chr(ord(c) ^ key), data))

    def deflate(self, data):
        pass

    def inflate(data):
        pass

    def decrypt(self, data):
        data = self.encode(data, self.response_key)[18:]
        return data

    def request_decrypt(self, data):
        data = self.encode(data, self.request_key)[18:]
        return data
    
    def encrypt(self, data):
        data = self.encode(data, self.request_key)
        _hash = hashlib.md5(self.checksumKey + data).digest()
        return self.version + _hash + data


class KYCrypt(object):

    def __init__(self):
        pass

    @property
    def cipher(self):
        return DES.new("@#h&^%8!", DES.MODE_CBC, "\x12\x34\x56\x78\x90\xab\xcd\xef")

    def encrypt(self, data):
        return self.cipher.encrypt(_pad_(data)).encode("base64")

    def decrypt(self, data):
        return _unpad_(self.cipher.decrypt(data.decode("base64")))

