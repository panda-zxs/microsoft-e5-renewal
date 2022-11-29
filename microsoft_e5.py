import json
import requests
import sys
import logging
from loguru import logger

LOGGING_LEVEL = logging.INFO
log_file_path = "./microsoft_e5.log"
log_format = "{time: YYYY-mm-dd HH:mm:ss.SSS} {message}"
LOG_HANDLERS = [
    {
        "sink": sys.stderr,
        "level": LOGGING_LEVEL,
        "format": "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> <blue>{message}</blue>"
    },
    {
        "sink": log_file_path,
        "rotation": "12:00",
        "retention": "1 week",
        "encoding": 'utf-8',
        "enqueue": True,
        "format": log_format,
    }
]


class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


def configure_logger() -> None:
    logging.root.handlers = [InterceptHandler()]
    logging.root.setLevel("DEBUG")

    # Remove all log handlers and propagate to root logger
    for name in logging.root.manager.loggerDict.keys():
        logging.getLogger(name).handlers = []
        logging.getLogger(name).propagate = True

    # Configure logger (again) if gunicorn is not used
    logger.configure(handlers=LOG_HANDLERS)


configure_logger()


def load_payload():
    with open("./payload.json", "r") as f:
        return json.load(f)


def authorize(code, redirect_uri, client_id, client_secret, tenant):
    """
     OAUTH 注册
     获取 code
     url = "https://login.microsoftonline.com/e3e7b845-98f1-4954-8f12-24b21c9ad731/oauth2/v2.0/authorize?client_id=8ec457a4-40a2-4cad-9c11-7e3b41eb3787&response_type=code&redirect_uri=http://localhost:8000/receive&response_mode=query&scope=offline_access%20user.read%20mail.readwrite%20mail.send&state=12345"
     http://localhost:8000/receive?
     code=

     0.AVYARbjn4_GYVEmPEiSyHJrXMaRXxI6iQK1MnBF-O0HrN4efALQ.AgABAAIAAAD--DLA3VO7QrddgJg7WevrAgDs_wQA9P9LEBuqyXzXK6JxQm2eKiNPnnPJV25TKgtaSQJX84JyLTOBx6XiyWiP8MQbs-y3Bw9mbvLNaU1AEMJAbYXw1yyMKGDJmH-qntO-dUcgMc6wTV_K4YGuHAjRpOOF0eBPVZl1Oi9uOKe-olIK1bx1kmH_ybilWZ27YnNopZK7ZPV84-SfBDapUF60SS_9-xsQRFXiYLScxvJcw7E16wtMJSkzTdO8pHHVeWS53XYObgcvABIkT2uEthsKJuiyYiIkdJghdI6K9Y7nFyOTTpENPAxwHCIMpWScy6OlEOVPiButrqEmq371Qlz6jIjSyU4eUZfT-cWInBZYfYoK76qn5mNcZcyvyIKRz9f0A39Cj0kSbvqOVaYI9PLpZo9Bq_AnA3vovKfsqPJ0ZalgqrJZWr4hSC4O3yu4oW5KZx78EGdzFiX5ud3XjobMLNWrVvSSagc2Eil6HCgOCyGtGa9Bi4LLNCc5Sv8xrD7DMLdUPqSLxPcyEQQ0xyKps4vw84VCjjTL4Ee43_oh2VnI9akil4GyRfQ7QeTMy7Rtu3-pOK4vfNzrhIeHLWpZ8zOPoC8QogNn2ItfLoboZMX9pYiYaFkASJ50ZfMPtr4cVDPtnxUC3OIJyuMG1v6doYwq5RpU9F0O-7284ic3t8aZGTHTJbbGmS05rGMhtEfC0w8bzpbYbr41Cym4aenjvuqy2TgvSykiCE2ZRVWzgT8m7BNUNcLe58I

     &state=12345&session_state=ee2568dd-4eb1-4a5b-a69a-79cfa1ecf727#
     放入 code 到 dt 中
    """

    # code = 0.AVYARbjn4_GYVEmPEiSyHJrXMaRXxI6iQK1MnBF-O0HrN4efALQ.AgABAAIAAAD--DLA3VO7QrddgJg7WevrAgDs_wQA9P9LEBuqyXzXK6JxQm2eKiNPnnPJV25TKgtaSQJX84JyLTOBx6XiyWiP8MQbs-y3Bw9mbvLNaU1AEMJAbYXw1yyMKGDJmH-qntO-dUcgMc6wTV_K4YGuHAjRpOOF0eBPVZl1Oi9uOKe-olIK1bx1kmH_ybilWZ27YnNopZK7ZPV84-SfBDapUF60SS_9-xsQRFXiYLScxvJcw7E16wtMJSkzTdO8pHHVeWS53XYObgcvABIkT2uEthsKJuiyYiIkdJghdI6K9Y7nFyOTTpENPAxwHCIMpWScy6OlEOVPiButrqEmq371Qlz6jIjSyU4eUZfT-cWInBZYfYoK76qn5mNcZcyvyIKRz9f0A39Cj0kSbvqOVaYI9PLpZo9Bq_AnA3vovKfsqPJ0ZalgqrJZWr4hSC4O3yu4oW5KZx78EGdzFiX5ud3XjobMLNWrVvSSagc2Eil6HCgOCyGtGa9Bi4LLNCc5Sv8xrD7DMLdUPqSLxPcyEQQ0xyKps4vw84VCjjTL4Ee43_oh2VnI9akil4GyRfQ7QeTMy7Rtu3-pOK4vfNzrhIeHLWpZ8zOPoC8QogNn2ItfLoboZMX9pYiYaFkASJ50ZfMPtr4cVDPtnxUC3OIJyuMG1v6doYwq5RpU9F0O-7284ic3t8aZGTHTJbbGmS05rGMhtEfC0w8bzpbYbr41Cym4aenjvuqy2TgvSykiCE2ZRVWzgT8m7BNUNcLe58I
    # redirect_uri = "http://localhost:8000/receive"
    # client_secret = "YX_8Q~uL_OWUqqInNuYWJJwY6PljMvfAi5z1tcnh"
    # client_id = "8ec457a4-40a2-4cad-9c11-7e3b41eb3787"
    # tenant = "e3e7b845-98f1-4954-8f12-24b21c9ad731"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    dt = {
        "client_id": client_id,
        "scope": "user.read mail.readwrite mail.send",
        "code": code,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code",
        "client_secret": client_secret,
    }
    url = "https://login.microsoftonline.com/{tenant}/oauth2/v2.0/token".format(tenant=tenant)
    rst = requests.post(url, headers=headers, data=dt)
    payload = rst.json()
    if "access_token" in payload.keys():
        logger.info("{}".format("注册成功"))
        with open("./payload.json", "w") as f:
            json.dump(rst.json(), f)


def refresh_token():
    url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    refresh_token = load_payload()["refresh_token"]
    dt = {
        "client_id": "8ec457a4-40a2-4cad-9c11-7e3b41eb3787",
        "scope": "user.read mail.readwrite mail.send",
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
        "client_secret": "YX_8Q~uL_OWUqqInNuYWJJwY6PljMvfAi5z1tcnh",
    }
    rst = requests.post(url=url, headers=headers, data=dt)
    payload = rst.json()
    if "access_token" in payload.keys():
        logger.info("{}".format("更新token成功"))
        with open("./payload.json", "w") as f:
            json.dump(rst.json(), f)


def get_access_token():
    dt = load_payload()
    return " ".join([dt["token_type"], dt["access_token"]])


def get_user(access_token=None):
    if not access_token:
        access_token = get_access_token()
    headers = {
        "Authorization": access_token
    }
    rst = requests.get("https://graph.microsoft.com/v1.0/me", headers=headers)
    payload = rst.json()
    if rst.status_code == 200:
        logger.info("{}".format("获取用户信息成功"))
    else:
        logger.info("{}".format("获取用户信息失败"))
    return payload


def read_mail(access_token=None):
    if not access_token:
        access_token = get_access_token()
    headers = {
        "Authorization": access_token
    }
    rst = requests.get("https://graph.microsoft.com/v1.0/me/messages", headers=headers)
    payload = rst.json()
    if rst.status_code == 200:
        logger.info("{}".format("读取邮件列表成功"))
    else:
        logger.info("{}".format("读取邮件列表失败"))
    return payload


def read_mail_info(access_token=None):
    if not access_token:
        access_token = get_access_token()
    mail_list = read_mail(access_token=access_token)
    mail_id = mail_list["value"][0]["id"]
    headers = {
        "Authorization": access_token
    }
    rst = requests.get("https://graph.microsoft.com/v1.0/me/messages/{mail_id}".format(mail_id=mail_id),
                       headers=headers)
    payload = rst.json()
    if rst.status_code == 200:
        logger.info("{}".format("读取邮件详情成功"))
    else:
        logger.info("{}".format("读取邮件详情失败"))
    return payload


def update_mail_read(access_token=None):
    if not access_token:
        access_token = get_access_token()
    mail_list = read_mail(access_token=access_token)
    mail_id = mail_list["value"][0]["id"]

    headers = {
        "Authorization": access_token,
        "Content-type": "application/json",
    }
    data = {
        "isRead": True
    }
    rst = requests.patch("https://graph.microsoft.com/v1.0/me/messages/{mail_id}".format(mail_id=mail_id),
                         headers=headers, json=data)
    payload = rst.json()
    if rst.status_code == 200:
        logger.info("{}".format("更新第一封邮件为已读成功"))
    else:
        logger.info("{}".format("更新第一封邮件为已读失败"))
    return payload


def send_mail(access_token=None):
    if not access_token:
        access_token = get_access_token()
    headers = {
        "Authorization": access_token,
        "Content-type": "application/json",
    }
    data = {
        "message": {
            "subject": "Meet for lunch?",
            "body": {
                "contentType": "Text",
                "content": "The new cafeteria is open."
            },
            "toRecipients": [
                {
                    "emailAddress": {
                        "address": "zxs45396622@gmail.com"
                    }
                }
            ],
            "ccRecipients": [
                {
                    "emailAddress": {
                        "address": "zxs45396622@gmail.com"
                    }
                }
            ]
        },
        "saveToSentItems": False
    }
    rst = requests.post("https://graph.microsoft.com/v1.0/me/sendMail",
                        headers=headers, json=data)
    if rst.status_code == 202:
        logger.info("{}".format("发送邮件成功"))
    else:
        logger.info("{}".format("发送邮件失败"))
    return rst.status_code


if __name__ == "__main__":
    # 使用前请相关文档 https://learn.microsoft.com/zh-cn/graph/auth/auth-concepts?view=graph-rest-1.0
    # 配置Web 重定向 URI 为本地网址用于获取 code 例如 http://localhost:8000/receive
    # ============================================================
    # 第一次注册
    # authorize()
    # ============================================================
    # 通过脚本完成读取用户，邮件读取、标记、发送等操作以完成续签目的
    logger.info("===============开始===============")
    refresh_token()
    token = get_access_token()
    get_user(token)
    read_mail(token)
    update_mail_read(token)
    send_mail(token)
    logger.info("===============完成===============")
