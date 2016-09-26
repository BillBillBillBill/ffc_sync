# coding: utf-8
from peewee import *
from playhouse.sqlite_ext import SqliteExtDatabase


class MOZCookies(Model):
    """
    CREATE TABLE moz_cookies (
    id INTEGER PRIMARY KEY,
    baseDomain TEXT,
    originAttributes TEXT NOT NULL DEFAULT '',
    name TEXT,
    value TEXT,
    host TEXT,
    path TEXT,
    expiry INTEGER,
    lastAccessed INTEGER,
    creationTime INTEGER,
    isSecure INTEGER,
    isHttpOnly INTEGER,
    appId INTEGER DEFAULT 0,
    inBrowserElement INTEGER DEFAULT 0,
    CONSTRAINT moz_uniqueid UNIQUE (name, host, path, originAttributes)
    )
    """
    id = IntegerField(primary_key=True)
    baseDomain = TextField()
    originAttributes = TextField(null=False, default='')
    name = TextField()
    value = TextField()
    host = TextField()
    path = TextField()
    expiry = IntegerField()
    lastAccessed = IntegerField()
    creationTime = IntegerField()
    isSecure = BooleanField()
    isHttpOnly = BooleanField()
    appId = IntegerField(default=0)
    inBrowserElement = BooleanField(default=False)

    class Meta:
        db_table = 'moz_cookies'
        database = SqliteExtDatabase('default.sqlite')
        indexes = (
            # create a unique index
            (('name', 'host', 'path', 'originAttributes'), True),
            (('baseDomain', 'originAttributes'), False),
            (('creationTime', ), False),
        )

    @classmethod
    def insert_one(cls, cookie_obj):
        if cookie_obj.get('id'):
            cookie_obj.pop('id')
        try:
            cls.create(**cookie_obj)
            return True
        except IntegrityError:
            # update
            query = cls.select().where(
                (cls.name == cookie_obj['name']) &
                (cls.host == cookie_obj['host']) &
                (cls.path == cookie_obj['path']) &
                (cls.originAttributes == cookie_obj['originAttributes']) &
                (cls.creationTime < cookie_obj['creationTime'])
            )
            if query.count() == 1:
                cookie = query[0]
                # fuck peewee
                for k, v in cookie_obj.items():
                    cookie.__setattr__(k, v)
                cookie.save()
                return True
            else:
                return False

    @classmethod
    def insert_many(cls, cookie_objs):
        succ_count = 0
        for cookie_obj in cookie_objs:
            if cls.insert_one(cookie_obj):
                succ_count += 1
        return succ_count

    def to_json(self):
        return {
            # 'id': self.id,
            'baseDomain': self.baseDomain,
            'originAttributes': self.originAttributes,
            'name': self.name,
            'value': self.value,
            'host': self.host,
            'path': self.path,
            'expiry': self.expiry,
            'lastAccessed': self.lastAccessed,
            'creationTime': self.creationTime,
            'isSecure': self.isSecure,
            'isHttpOnly': self.isHttpOnly,
            'appId': self.appId,
            'inBrowserElement': self.inBrowserElement,
        }

    @classmethod
    def get_latest_creationTime(cls):
        """
        获取最新一条记录的创建时间
        """
        query = cls.select().order_by(cls.creationTime.desc()).limit(1)
        if len(query) == 1:
            return query[0].creationTime
        return 0

    @classmethod
    def get_cookies_after(cls, creationTime=0):
        """
        获取指定时间后的所有记录
        """
        query = cls.select().where(cls.creationTime > creationTime).order_by(cls.creationTime.desc())
        return [cookie.to_json() for cookie in query]

    @staticmethod
    def set_db(db_path):
        MOZCookies._meta.database.database = db_path


if __name__ == '__main__':
    from IPython import embed
    embed()
