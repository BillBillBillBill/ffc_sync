# coding: utf-8
from config import SECRET_KEY
from flask import Flask, request, jsonify
from model import MOZCookies


app = Flask(__name__)


@app.route('/sync', methods=['POST'])
def sync():
    data = request.json
    secret_key = data.get('secret_key')  # 暂时先这样验证
    if secret_key != SECRET_KEY:
        return jsonify({'error_msg': 'secret_key not match!'})
    cookies = data.get('cookies')
    final_time = data.get('final_time')
    update_count = MOZCookies.insert_many(cookies)
    new_cookies = MOZCookies.get_cookies_after(final_time)
    return jsonify(
        {
            'cookies': new_cookies,
            'update_count': update_count,
        }
    )


def ensure_db():
    MOZCookies.set_db('%s.sqlite' % SECRET_KEY)
    if not MOZCookies.table_exists():
        MOZCookies.create_table()


if __name__ == '__main__':
    ensure_db()
    app.run(host='0.0.0.0', debug=True, threaded=True)
