from requests import Session
import requests
from bs4 import BeautifulSoup
from .encrypt import *
from typing import Dict
from base64 import b64encode,b64decode
from Crypto.Cipher import AES,DES
from Crypto.Util.Padding import pad



headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.114 Safari/537.36"
}
# url = "http://authserver.cqu.edu.cn/authserver/login"
url = "https://sso.cqu.edu.cn/login"


def get_formdata(html: str, username: str, password: str) -> Dict:
    """生成登录表单
    """
    soup = BeautifulSoup(html, 'html.parser')
    croypto = soup.find(id="login-croypto").text
    login_page_flowkey = soup.find(id="login-page-flowkey").text
    _eventId = 'submit'

    passwd_encrypted = b64encode(DES.new(b64decode(croypto),DES.MODE_ECB).encrypt \
              (pad(password.encode(),8,style='pkcs7')))
    passwd_encrypted = str(passwd_encrypted,encoding='utf-8')


    # 传入数据进行统一认证登录
    return {
        'username': str(username),
        'type': 'UsernamePassword',
        'password': passwd_encrypted,
        '_eventId': _eventId,
        'geolocation': '',
        'execution': login_page_flowkey,
        'croypto':croypto,
    }


def login(username: str, password: str) -> Session:
    """单点登录
    """
    session = requests.session()

    login_page = session.get(
        url=url,
        params=None,
        allow_redirects=False,
        timeout=10
        ) 

    # 构建登录表单，这里不考虑验证码的情况
    formdata = get_formdata(login_page.text, username, password)

    login_response = session.post(url=url, data=formdata, headers=headers, allow_redirects=False,timeout=10)
    # 重定向到目标服务
    session.get(url=login_response.headers['Location'], headers=headers, allow_redirects=False,timeout=10)
    return session
