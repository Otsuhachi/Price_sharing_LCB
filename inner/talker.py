import re
import threading
import time
from datetime import datetime, timedelta

from inner.loader import Loader
from inner.responder import AddResponder, ProductResponder


class Talker:
    """文字列を受け取り、それに応じた処理を行います。
    特定のパターンに一致する場合には商品をデータベースに登録する動作を行します。
    一致しない場合は商品検索モードで動作します。


    Attributes:
        users: 現在処理を行っている最中のユーザーの辞書です。
        actions: アクションを行う反応パターンです。
    """
    def __init__(self):
        """文字列を受け取り、処理を返します。

        反応パターンを読み込みます。
        ユーザーの辞書を用意します。
        定期的にタイムアウトしたユーザーを辞書から削除します。
        """
        self.__actions = Loader().actions
        self.__users = {}
        self.__th = threading.Thread(
            target=lambda: self.schedule(30, self.check_timeout, False))
        self.__th.setDaemon(True)
        self.__th.start()

    def dialogue(self, user_id, text):
        """ユーザーIDと文字列を受け取り、ユーザー毎に保持しているResponderからの応答を返します。

        Args:
            user_id (str): ユーザーID。
            text (str): 文字列。

        Returns:
            str: Responderからの応答。
        """
        self.entry_user(user_id, text)
        user = self.users[user_id]
        responder = user['responder']
        res = responder.response(text)
        if responder.state == 'end':
            self.delete_user(user_id)
        return res

    def entry_user(self, user_id, text):
        """ユーザーを登録します。
        受け取ったuser_idをキーにします。
        受け取った文字列を基にResponder, status, timeoutを値にします。

        Args:
            user_id (str): ユーザーID.
            text (str): 文字列。
        """
        self.users.setdefault(user_id, {
            'responder': None,
            'status': None,
            'timeout': None
        })
        self.set_status(user_id, text)
        self.set_responder(user_id)
        self.set_timeout(user_id)

    def set_responder(self, user_id):
        """ユーザーのstatusに応じてResponderを生成し、保持します。

        Args:
            user_id (str): ユーザID。
        """
        user = self.users[user_id]
        if user['responder'] is not None:
            return
        status = user['status']
        if status == 'add':
            responder = AddResponder()
        elif status == 'products':
            responder = ProductResponder()
        user['responder'] = responder

    def set_timeout(self, user_id, **timeout):
        """ユーザーにタイムアウトを設定します。

        Args:
            user_id (str): ユーザーID。
        """
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
        """ユーザーにstatusを設定します。

        Args:
            user_id (str): ユーザーID。
            text (str): 文字列。
        """
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
        """usersに登録されているユーザーのtimeoutを確認し、過ぎていればそのユーザーの登録を解除します。
        """
        del_users = []
        for user in self.users:
            timeout = self.users[user]['timeout']
            if timeout < datetime.now():
                del_users.append(user)
                print(f"delete: {user}")
        for user in del_users:
            self.delete_user(user)

    def delete_user(self, user_id):
        """ユーザーを削除します。
        Responderを保持している場合は閉じてから削除します。

        Args:
            user_id (str): ユーザーID。
        """
        if user_id in self.users:
            responder = self.users[user_id]['responder']
            if responder is not None:
                responder.exit()
            del self.users[user_id]

    def schedule(self, interval, f, wait=True):
        """指定した関数を定期的に実行するスレッドを生成します。

        Args:
            interval (int): 実行間隔。
            f (func): 実行する関数。
            wait (bool, optional): 実行中に待機するかどうか。
        """
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
        """ユーザーを登録しておく辞書です。

        Returns:
            dict: ユーザーを登録しておく辞書。
        """
        return self.__users

    @property
    def actions(self):
        """反応する特別な文字列の辞書です。

        Returns:
            dict: 反応する特別な文字列の辞書。
        """
        return self.__actions
