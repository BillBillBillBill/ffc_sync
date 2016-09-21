# coding: utf-8
from config import SECRET_KEY
import requests
import time
from model import MOZCookies


SYNC_API = 'http://localhost:5000/sync'


def start_sync():
    sync_count = 0
    while True:
        try:
            if sync_count == 0:
                # 第一次同步 全推 全拉
                final_time = 0
                cookies = MOZCookies.get_cookies_after(0)
                print 'First time to sync, please wait a moment'
            else:
                cookies = MOZCookies.get_cookies_after(final_time)

            print 'client upload cookies count: %d' % len(cookies)

            ret = requests.post(
                SYNC_API,
                json={
                    'secret_key': SECRET_KEY,
                    'cookies': cookies,
                    'final_time': final_time
                }
            )

            data = ret.json()
            return_cookies = data['cookies']
            print 'server update cookies count: %d' % data['update_count']
            print 'server return cookies count: %d' % len(return_cookies)

            # 更新本地cookie
            insert_count = MOZCookies.insert_many(return_cookies)
            if insert_count > 0 or sync_count == 0:
                final_time = MOZCookies.get_latest_creationTime()

            # 暂停一秒再继续
            time.sleep(0.03)
            sync_count += 1
            print 'sync %d times' % sync_count
        except Exception, e:
            print 'oops! something wrong happend: %s', e.message
            pass
        except KeyboardInterrupt:
            break
    print 'Bye'


if __name__ == '__main__':
    start_sync()
