from flask import request

def querystring():
    qs = request.query_string.decode()
    return f'?{qs}' if len(qs) > 0 else ''
