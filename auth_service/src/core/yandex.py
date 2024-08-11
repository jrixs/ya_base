from fastapi.security.oauth2 import OAuth2AuthorizationCodeBearer
from pydantic_settings import BaseSettings


class YaSettings(BaseSettings):

    YANDEX_CLIENT_ID = "3f762396a65b42198d13d124478ee921"
    YANDEX_CLIENT_SECRET = "ca912fb4beba408ba78952e623d9dec0"
    YANDEX_AUTH_URL = "https://oauth.yandex.ru/authorize"
    YANDEX_TOKEN_URL = "https://oauth.yandex.ru/token"
    YANDEX_USERINFO_URL = "https://login.yandex.ru/info"

ya_settings = YaSettings()

redirect_uri = "https://oauth.yandex.ru/ya_login"

'''
oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl=YANDEX_AUTH_URL,
    tokenUrl=YANDEX_TOKEN_URL
)
'''