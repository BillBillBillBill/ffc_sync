# coding: utf-8
from config import SYNC_KEY, SYNC_API
import requests
import time
import os
import platform
from getpass import getuser
from model import MOZCookies


FF_COOKIE_DIR = {
    'Windows': 'C:\Users\%s\AppData\Roaming\Mozilla\Firefox\Profiles',
    'Linux': '/home/%s/.mozilla/firefox'
}


def start_sync(cookie_db_path):
    MOZCookies.set_db(cookie_db_path)
    sync_count = 0
    final_time = 0
    while True:
        try:
            print '========The %d time to sync=========' % sync_count
            if sync_count == 0:
                # 第一次同步 全推 全拉
                upload_cookies = MOZCookies.get_cookies_after(0)
                print 'First time to sync, please wait a moment'
            else:
                upload_cookies = MOZCookies.get_cookies_after(final_time)

            upload_cookies_count = len(upload_cookies)
            print 'client upload cookies count: %d' % upload_cookies_count

            ret = requests.post(
                SYNC_API,
                json={
                    'secret_key': SYNC_KEY,
                    'cookies': upload_cookies,
                    'final_time': final_time
                }
            )

            data = ret.json()
            return_cookies = data['cookies']
            return_cookies_count = len(return_cookies)
            print 'server update cookies count: %d' % data['update_count']
            print 'server return cookies count: %d' % return_cookies_count

            # 更新本地cookie
            insert_count = MOZCookies.insert_many(return_cookies)
            print 'client update cookies count: %d' % insert_count
            if upload_cookies_count > 0:
                final_time = MOZCookies.get_latest_creationTime()

            # 暂停一秒再继续
            time.sleep(1)
            sync_count += 1
        except Exception, e:
            print 'oops! something wrong happend: %s' % e.message
            pass
        except KeyboardInterrupt:
            break
    print 'Bye'


def get_cookie_db_path():
    system_type = platform.system()
    username = getuser()
    print 'current user: %s' % username
    firefox_cookie_dir = FF_COOKIE_DIR.get(system_type)
    if not firefox_cookie_dir:
        print 'Your system %s is not supported' % system_type
        return
    cookie_parent_dir = firefox_cookie_dir % username
    dirs = filter(lambda f: 'default' in f, os.listdir(cookie_parent_dir))
    if not dirs:
        print 'Dir %s is not existed' % cookie_parent_dir
        return
    cookie_db_path = os.path.join(cookie_parent_dir, dirs[0], 'cookies.sqlite')
    if not os.path.exists(cookie_db_path):
        print 'cookie_db_path %s is not existed' % cookie_db_path
        return
    return cookie_db_path


if __name__ == '__main__':
    cookie_db_path = get_cookie_db_path()
    if cookie_db_path:
        print 'cookie_db_path: %s' % cookie_db_path
        start_sync(cookie_db_path)
    else:
        print 'bye'
