import json
import traceback
import urllib
import urlparse
import time

import requests
from gevent.lock import BoundedSemaphore

from CryptUtils import Account


__author__ = 'nk'

# Debugging
proxies = {"http": "http://127.0.0.1:48888"}


class LibMLK(object):
    def __init__(self, serverIP, Plist):
        self.serverIP = serverIP
        self.baseUrl = "http://%s/" % serverIP
        self.crypt = Account(Plist.userID, Plist.devideToken)
        self.mlkLock = BoundedSemaphore(200)
        self.IID = Plist.iid
        self.VID = Plist.vid


    def __init__(self):
        pass

    @property
    def headers(self):
        return {
            "VID": self.VID,
            "PID": "-",
            "IID": self.IID,
            "DEVICE_INFO": "iPad2,1:::iPhone OS 8.1.2",
            "Device": "ios",
            "AppVersion": 28,
            "APP_ID_3": self.crypt.deviceToken,
            "APP_ID_2": self.crypt.hashedUserID,
            "APP_ID_1": self.crypt.cryptedUserID,
            "Encrypted": True,
            "User-Agent": "toto/1.1.25.2 CFNetwork/711.1.16 Darwin/14.0.0",
            "Accept-Language": "zh-cn",
            "Accept": "application/json"
        }

    def _post(self, url, params={}, data={}):
        data["_method"] = "GET"
        data = urllib.urlencode(data)
        data = self.crypt.encrypt(data)
        url = urlparse.urljoin(self.baseUrl, url)
        if len(params) > 0:
            e = self.crypt.encrypt(urllib.urlencode(params)).encode("base64").replace("\n", "")
            url = "%s?e=%s" % (url, e)
        ret = None
        try:
            self.mlkLock.acquire()
            ret = requests.post(url, data=data, headers=self.headers, proxies=proxies)
        except:
            traceback.print_exc()
        finally:
            self.mlkLock.release()
        if ret is None:
            raise BaseException()
        if "encrypted" in ret.headers and ret.headers["encrypted"] == "true":
            rtn = self.crypt.decrypt(ret.content)
        else:
            rtn = ret.content
        return rtn

    def get(self, url, params={}, data={}):
        url = urlparse.urlparse(url)
        path = url.path
        query = dict(urlparse.parse_qsl(url.query))
        query.update(params)
        return self._post(path, params=query, data=data)

    def setUsername(self, name):
        ret = self._post("users/update", data={"user_name": name})
        self.user_name = name
        return json.loads(ret)

    def finishTutorial(self):
        ret = self._post("users/update",
                         data={"user_name": self.user_name, "tutorial_finish": True})
        return json.loads(ret)

    def getMessages(self, page_type="Home"):
        params = {
            "last_read_at": int(time.time()),
            "page_type": page_type
        }
        ret = self._post("users/messages", params=params)
        return json.loads(ret)

    def getStages(self):
        ret = self._post("stages")
        return json.loads(ret)

    def getAreas(self, stage_id):
        ret = self._post("areas", params={"stage_id": stage_id})
        return json.loads(ret)

    def getMonsters(self):
        ret = self._post("user_monsters")
        return json.loads(ret)

    def getDecks(self):
        ret = self._post("user_decks")
        return json.loads(ret)

    def getUnits(self):
        ret = self._post("user_units")
        return json.loads(ret)

    def receiveLoginBonus(self):
        ret = self._post("users/receive_login_bonus")
        return json.loads(ret)

    def getLoginRewardList(self):
        ret = self._post("accu_login_activity")
        return json.loads(ret)

    def receiveLoginReward(self, day):
        params = {"day": day}
        ret = self._post("accu_login_activity/fetch_rewards", params=params)
        return json.loads(ret)

    def getRewardList(self):
        ret = self._post("user_presents")
        return json.loads(ret)

    def reward(self, uuid):
        params = {"uuid": uuid}
        ret = self._post("user_presents/receive", params)
        return json.loads(ret)

    def rewardAll(self):
        ret = self._post("user_presents/receive")
        return json.loads(ret)

    def getUserData(self):
        ret = self._post("users/preset_data.json?tutorial_session=true")
        return json.loads(ret)

    def gacha(self, gacha_id, num):
        params = {"id": gacha_id, "count": num}
        ret = self._post("gachas/execute", params=params)
        return json.loads(ret)

    def getUnitList(self):
        ret = self._post("user_units")
        return json.loads(ret)

    def quest(self, quest_id, party_id="001", difficulty_id="normal"):
        params = {
            "base": "Quest/Quest",
            "difficulty_id": difficulty_id,
            "id": quest_id,
            "mode": "quest",
            "name": "Quest",
            "party_id": party_id,
            "tipsLoading": "true",
        }
        ret = self._post("quests/execute/%s.json" % quest_id, params=params)
        ret = json.loads(ret)
        result_url = ret["result_url"]
        if "ap_use_url" in ret:
            ap_use_url = ret["ap_use_url"]
            self.get(ap_use_url)
        time.sleep(30)
        ret = self.get(result_url, params={"time": "27.1234"})
        return ret

