from datetime import datetime
import re
import requests
import plugins
from plugins import *
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from common.log import logger

BASE_URL_ALAPI = "https://v2.alapi.cn/api/"
BASE_URL_XIAROU = "http://api.suxun.site/api/"


@plugins.register(name="pgsh",
                  desc="胖乖生活的一些功能",
                  version="1.0",
                  author="masterke",
                  desire_priority=100)
class pgsh(Plugin):
    def __init__(self):
        super().__init__()
        self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
        logger.info(f"[{__class__.__name__}] inited")
    def on_handle_context(self, e_context: EventContext):
        self.context = e_context['context']
        self.e_context = e_context
        self.channel = e_context['channel']
        self.message = e_context["context"].content
        # =======================插件处理流程==========================
        logger.info(f"[{__class__.__name__}] 收到消息: {self.message}")
        if self.context.type == ContextType.TEXT:
            if self.message.startswith('胖乖积分查询'):
                result, result_type = self.pgsh_query()
            elif self.message.startswith('胖乖验证码发送'):
                result, result_type = self.pgsh_send_code()
            elif self.message.startswith('胖乖密钥获取'):
                result, result_type = self.pgsh_get_token()
            else:
                return
        else:
            return
        
        reply = Reply()
        if result != None:
            reply.type = result_type
            reply.content = result
            self.e_context["reply"] = reply
            self.e_context.action = EventAction.BREAK_PASS
        else:
            reply.type = ReplyType.ERROR
            reply.content = "获取失败,等待修复⌛️"
            self.e_context["reply"] = reply
            self.e_context.action = EventAction.BREAK_PASS
    # =======================函数定义部分==========================
    def pgsh_query(self):
        pattern = r"胖乖积分查询@[0-9a-z]{32}$"
        match = re.search(pattern, self.message)
        if match:
            keyword, token = self.message.split("@")
        else:
            return self.get_help_text()
        try:
            url = "https://userapi.qiekj.com/user/balance"
            payload = {'token': token}
            headers = {
                        "Authorization":"",
                        "Version":"1.50.0",
                        "channel":"android_app",
                        "phoneBrand":"OnePlus",
                        "Content-Type":"application/x-www-form-urlencoded;charset=UTF-8",
                        "Content-Length":"30",
                        "Host":"userapi.qiekj.com",
                        "Connection":"Keep-Alive",
                        "Accept-Encoding":"gzip",
                        "User-Agent":"okhttp/3.14.9"
                    }
            response = requests.request("POST", url, headers=headers, data=payload)
            rjson = response.json()
            if response.status_code == 200 and rjson['code'] == 0:
                return f"🎉查询成功！\n==========\n\n剩余：{rjson['data']['integral']}积分\n大约：{rjson['data']['integralAmount']}元", ReplyType.TEXT
            elif rjson['code'] == 2:
                return f"❌查询失败！\n==========\n\n失败原因：【token过期】", ReplyType.TEXT
            else:
                return None, ReplyType.ERROR 
        except Exception as e:
            logger.info(f"[{__class__.__name__}] pgsh_query异常:{e}")
            return None, ReplyType.ERROR
        
    def pgsh_send_code(self):
        pattern = r"胖乖验证码发送@[0-9]{11}$"
        match = re.search(pattern, self.message)
        if match:
            keyword, phone_number = self.message.split("@")
        else:
            return self.get_help_text()
        try:
            url = "https://userapi.qiekj.com/common/sms/sendCode"
            payload = {'phone': phone_number,'template': 'reg'}
            headers = {
                        "Authorization":"",
                        "Version":"1.50.0",
                        "channel":"android_app",
                        "phoneBrand":"OnePlus",
                        "Content-Type":"application/x-www-form-urlencoded;charset=UTF-8",
                        "Content-Length":"30",
                        "Host":"userapi.qiekj.com",
                        "Connection":"Keep-Alive",
                        "Accept-Encoding":"gzip",
                        "User-Agent":"okhttp/3.14.9"
                    }
            response = requests.request("POST", url, headers=headers, data=payload)
            rjson = response.json()
            if response.status_code == 200 and rjson['code'] == 0:
                return f"🎉发送成功！", ReplyType.TEXT
            else:
                return None, ReplyType.ERROR 
        except Exception as e:
            logger.info(f"[{__class__.__name__}] pgsh_send_code异常:{e}")
            return None, ReplyType.ERROR
    def pgsh_get_token(self):
        pattern = r"胖乖密钥获取@[0-9]{11}@[0-9]{4}$"
        match = re.search(pattern, self.message)
        if match:
            keyword, phone_number, verify_code = self.message.split("@")
        else:
            return self.get_help_text()
        try:
            url = "https://userapi.qiekj.com/user/reg"
            payload = {'channel': 'android_app','phone': phone_number,'verify': verify_code}
            headers = {
                        "Authorization":"",
                        "Version":"1.50.0",
                        "channel":"android_app",
                        "phoneBrand":"OnePlus",
                        "Content-Type":"application/x-www-form-urlencoded;charset=UTF-8",
                        "Content-Length":"49",
                        "Host":"userapi.qiekj.com",
                        "Connection":"Keep-Alive",
                        "Accept-Encoding":"gzip",
                        "User-Agent":"okhttp/3.14.9"
                    }
            response = requests.request("POST", url, headers=headers, data=payload)
            if response.status_code == 200:
                rjson = response.json()
                print(rjson)
                if rjson['code'] == 0:
                    token = rjson['data']['token']
                    return f"您的token是：\n{token}", ReplyType.TEXT
                elif rjson['code'] == 1001:
                    return f"❌获取失败！\n==========\n\n失败原因：【验证码错误】", ReplyType.TEXT
                else:
                    return None, ReplyType.ERROR
            else:
                return None, ReplyType.ERROR 
        except Exception as e:
            logger.info(f"[{__class__.__name__}] pgsh_get_token异常:{e}")
            return None, ReplyType.ERROR
    def get_help_text(self, **kwargs):
        help_text = f"【胖乖积分查询@token】查询剩余积分\n【胖乖验证码发送】", ReplyType.TEXT
        return help_text