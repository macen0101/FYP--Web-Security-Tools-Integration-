import json
from mitmproxy import http

def request(flow: http.HTTPFlow) -> None:
    data = {
        'url': flow.request.pretty_url,
        'method': flow.request.method,
        'headers': dict(flow.request.headers),
        'content': flow.request.content.decode('utf-8')
    }
    with open('requests.txt', 'a') as f:
        f.write(json.dumps(data))
        f.write('\n')

def response(flow: http.HTTPFlow) -> None:
    data = {
        'status_code': flow.response.status_code,
        'headers': dict(flow.response.headers),
        'content': flow.response.content.decode('utf-8')
    }
    with open('responses.txt', 'a') as f:
        f.write(json.dumps(data))
        f.write('\n')