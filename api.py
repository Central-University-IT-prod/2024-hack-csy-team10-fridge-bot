import requests

api_url = 'http://localhost:3000/{}/'


def api(method, endpoint, **kwargs):
    resp = requests.request(method, api_url.format(endpoint), **kwargs)
    resp.raise_for_status()
    return resp


def login(username: str, password: str):
    resp = api("POST", f"auth/token/login", data={'username': username, 'password': password}).json()
    return resp


def get_all_fridges(token):
    resp = api("GET", f"fridges", headers={'Authorization': f'Token {token}'}).json()
    return resp


def send_qr(text, fridge_id, token):
    resp = api("POST", f"products/{fridge_id}/push_products_from_receipt", data={'q': text}, headers={'Authorization': f'Token {token}'}).json()
    return resp
