#!/usr/bin/env python
import requests
import time
import json


class Notifier(object):
    def __init__(self, corp_id, corp_secret, agent_id):
        self.corp_id = corp_id
        self.agent_id = agent_id
        self.corp_secret = corp_secret
        self._access_token = None
        self.expires_at = time.time()

    def access_token(self):
        if self._access_token and self.expires_at > time.time():
            return self._access_token

        ret = self.get_access_token()
        self._access_token = ret['access_token']
        self.expires_at = time.time() + int(ret['expires_in']) - 300
        return self._access_token

    def get_access_token(self):
        url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken'
        resp = requests.get(url, params={
            'corpid': self.corp_id,
            'corpsecret': self.corp_secret,
        })
        return resp.json()

    def notify(self, content):
        url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send'
        requests.post(
            url,
            params={'access_token': self.access_token()},
            data=json.dumps({
                "touser": "@all",
                "msgtype": "text",
                "agentid": self.agent_id,
                "text": {
                    "content": content
                },
                "safe": "0"
            }, ensure_ascii=False))
