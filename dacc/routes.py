from dacc import dacc
from flask import request


@dacc.route('/')
def index():
    return "Hello, World!"


@dacc.route('/contribute', methods=['POST'])
def contribute():
    request_data = request.get_json()
    print(request_data)
    return "ok"
