import re
import threading
import time
from datetime import datetime, timedelta

from inner.loader import Loader
from inner.responder import AddResponder, ProductsResponder


class Talker:
    def __init__(self):
        self.__actions = Loader().actions
        self.__users = {}
        self.__th = threading.Thread(
            target=lambda: self.schedule(30, self.check_timeout, False))
        self.__th.setDaemon(True)
        self.__th.start()

    def dialogue(self, user_id, text):
        self.entry_user(user_id, text)
        user = self.users[user_id]
        responder = user['responder']
        res = responder.response(text)
        if responder.state == 'end':
            self.delete_user(user_id)
        return res

    def entry_user(self, user_id, text):
        self.users.setdefault(user_id, {
            'responder': None,
            'status': None,
            'timeout': None
        })
        self.set_status(user_id, text)
        self.set_responder(user_id)
        self.set_timeout(user_id)

    def set_responder(self, user_id):
        user = self.users[user_id]
        if user['responder'] is not None:
            return
        status = user['status']
        if status == 'add':
            responder = AddResponder()
        elif status == 'products':
            responder = ProductsResponder()
        user['responder'] = responder

    def set_timeout(self, user_id, **timeout):
        options = ('days', 'seconds', 'microseconds', 'milliseconds',
                   'minutes', 'hours', 'weeks')
        if not all(x in options for x in timeout):
            err = f"timeoutに不正な値が入力されています。初期値に設定されました。\n{timeout}"
            print(err)
            timeout = None
        if not timeout:
            timeout = {'minutes': 3}
        self.users[user_id]['timeout'] = datetime.now() + timedelta(**timeout)

    def set_status(self, user_id, text):
        user = self.users[user_id]
        for ptn in self.actions:
            matcher = re.search(ptn['pattern'], text)
            if matcher:
                user['status'] = ptn['status']
                break
        else:
            status = user['status']
            if status is None:
                status = 'products'
            user['status'] = status

    def check_timeout(self):
        del_users = []
        for user in self.users:
            timeout = self.users[user]['timeout']
            if timeout < datetime.now():
                del_users.append(user)
                print(f"delete: {user}")
        for user in del_users:
            self.delete_user(user)

    def delete_user(self, user_id):
        if user_id in self.users:
            responder = self.users[user_id]['responder']
            if responder is not None:
                responder.exit()
            del self.users[user_id]

    def schedule(self, interval, f, wait=True):
        base_time = time.time()
        next_time = 0
        while True:
            t = threading.Thread(target=f)
            t.start()
            if wait:
                t.join()
            next_time = ((base_time - time.time()) % interval) or interval
            time.sleep(next_time)

    @property
    def users(self):
        return self.__users

    @property
    def actions(self):
        return self.__actions
