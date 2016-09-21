# coding: utf-8
from config import SECRET_KEY
from flask import Flask, request, jsonify
from model import MOZCookies


app = Flask(__name__)


@app.route('/sync', methods=['POST'])
def sync():
    data = request.json
    secret_key = data.get('secret_key')  # 暂时先这样
    if secret_key != SECRET_KEY:
        return jsonify({'error_msg': 'secret_key not match!'})
    cookies = data.get('cookies')
    final_time = data.get('final_time')
    update_count = MOZCookies.insert_many(cookies)
    if final_time:
        new_cookies = MOZCookies.get_cookies_after(final_time)
    else:
        new_cookies = []
    return jsonify(
        {
            'cookies': new_cookies,
            'update_count': update_count,
        }
    )


def ensure_db():
    MOZCookies._meta.database.database = '%s.sqlite' % SECRET_KEY
    if not MOZCookies.table_exists():
        MOZCookies.create_table()


if __name__ == '__main__':
    ensure_db()
    app.run(debug=True, threaded=True)
