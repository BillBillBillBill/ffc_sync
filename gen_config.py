from hashlib import md5
import os


def gen_config():
    if raw_input("Are you sure to generate a new sync key?[Y/N]").lower() == "y":
        sync_key = md5(os.urandom(128)).hexdigest()
        sync_api = raw_input("Please enter the sync api:")
        with open("config.py", "w") as f:
            f.write("SYNC_KEY = '%s'\nSYNC_API = '%s'\n" % (sync_key, sync_api))
        print "Ok, please remember your sync key: %s" % sync_key


if __name__ == '__main__':
    gen_config()
