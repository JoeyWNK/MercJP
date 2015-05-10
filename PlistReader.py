import re

from biplist import readPlist, writePlist, InvalidPlistException, NotBinaryPlistException

from CryptUtils import Account

__author__ = 'nk'

patten = re.compile('^\w{8}-\w{4}-\w{4}-\w{4}-\w{12}$')


class PlistReader():
    def __init__(self, filename):
        self.read = readPlist(filename)
        if not self.read.get("VID"):
            text = raw_input("Please input VID:").upper()
            if patten.match(text):
                newlist = {
                    'VID': text,
                    'UUID': self.userid,
                    'DeviceToken': self.devicetoken,
                    'IID': self.iid
                }
                try:
                    newfile = raw_input("Please input new Plist file name:")
                    writePlist(newlist, newfile)
                    self.read = readPlist(newfile)
                except (InvalidPlistException, NotBinaryPlistException), e:
                    print "Fail to write File"
            else:
                print "Fail"

    def get(self, key):
        return self.read.get(key, str)

    @property
    def vid(self):
        return self.get("VID")

    @property
    def userid(self):
        return self.get("UUID")

    @property
    def devicetoken(self):
        return self.get("DeviceToken")

    @property
    def iid(self):
        return self.get("IID")


if __name__ == "__main__":
    # testing purpose
    inputfile = PlistReader(raw_input("Please input Plist file name:"))
    he = Account(inputfile.userid, inputfile.devicetoken)

    print he.cryptedUserID
    print he.hashedUserID
    print he.deviceToken
    print inputfile.iid
    print inputfile.vid



