#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import hashlib
import random

from LibMLK import LibMLK
from PlistReader import PlistReader


def calcDeviceID(username):
    return hashlib.md5(username).hexdigest()


def randomDeviceID():
    table = "0123456789abcdef"
    return "".join([random.choice(table) for i in range(16)])

if __name__ == "__main__":
    Plist = PlistReader("jp.co.happyelements.toto.plist")
    mlk = LibMLK("toto.hekk.org", Plist)
    print json.loads(mlk.get("/users/preset_data.json?tutorial_session=true"))["data"]["user"]["level"]
    rewardList = mlk.getRewardList()["data"]["user_presents"]

