import random
import time
from urllib.parse import quote
import hmac
import hashlib
import binascii
import base64


class Auth(object):
    def __init__(self, appid, SecretID, SecretKey, bucket, region, method, objectName, head="", parameters=""):
        """

        :param appid: 开发者访问 COS 服务时拥有的用户维度唯一资源标识，用以标示资源。
        :param SecretID: SecretID 是开发者拥有的项目身份识别 ID，用以身份认证
        :param SecretKey: SecretKey 是开发者拥有的项目身份密钥。
        :param bucket: 存储桶是 COS 中用于存储数据的容器，是用户存储在 Appid 下的第一级目录，每个对象都存储在一个存储桶中。
        :param region: 域名中的地域信息，枚举值：cn-east（华东），cn-north（华北），cn-south（华南），sg（新加坡）
        :param method: 指该请求的 HTTP 操作行为，例如 PUT/GET/DELETE，必须转为小写字符。
        :param objectName: 指该请求中的 URI 部分，即除去 http:// 协议和域名的部分（通常以 / 开始），并且不包含 URL 中的参数部分（通常以 ? 开始）。
        :param head: 指请求中的 HTTP 头部信息，用 key=value 的方式表达。头部的 key 必须全部小写，value 必须经过 URL Encode。如果有多个参数对可使用 & 连接。key值按字典序排序
        :param parameters: 指该请求中的参数部分（以 ? 开始的部分），用 key=value 的方式表达。
        """
        self.appid = appid
        self.SecretID = SecretID
        self.SecretKey = SecretKey
        self.bucket = bucket
        self.region = region

        self.method = method
        self.objectname = objectName
        self.parameters = parameters.encode('utf-8')
        self.head = head

        self.q_sign_time = int(time.time())
        self.q_key_time = self.q_sign_time + 60
        self.sh1hash_formatstring = ''

    def get_signkey(self):
        q_time = '%s;%s' % (self.q_sign_time, self.q_key_time)
        signkey = hmac.new(bytes(self.SecretKey,'utf-8'), bytes(q_time,'utf-8'), hashlib.sha1).hexdigest()
        return signkey

    def set_sh1hash_formatstring(self):
        format_method = self.method
        format_url = self.objectname
        format_parameters = self.parameters

        host = '%s-%s.%s.myqcloud.com' % (self.bucket, self.appid, self.region)
        format_head = {'host': host.encode('utf-8')}
        if self.head != "":
            headlist = self.head.split('&')
            for n in headlist:
                head = n.split('=')
                newlist = {head[0].lower(): head[1].encode('utf-8')}
                format_head.update(newlist)




        format_string = "%s\n%s\n%s\n%s" % (format_method, format_url, format_parameters, format_headers)
        self.sh1hash_formatstring = hashlib.sha1(format_string)

    def get_stringtosign(self):
        q_sign_time = '%s;%s' % (self.q_sign_time, self.q_sign_time)
        stringtosign = "sha1\n%s\n%s" % (q_sign_time, self.sh1hash_formatstring)
        return stringtosign

    def get_signature(self):
        signature = hmac.new(bytes(self.get_signkey()), bytes(self.get_stringtosign()), hashlib.sha1).hexdigest()
        return signature

    def get_authorization(self):
        signed_header_list = "host"
        t_tuple = (self.SecretID, self.q_sign_time, self.q_key_time, )
        authorization = "q-sign-algorithm=sha1&" \
                        "q-ak=%s&" \
                        "q-sign-time=%s&" \
                        "q-key-time=%s&" \
                        "q-header-list=<SignedHeaderList>&" \
                        "q-url-param-list=<SignedParameterList>&" \
                        "q-signature=<Signature>" % t_tuple


    # def __init__(self, appid, SecretID, SecretKey, bucket, file='', currentTime='', expiredTime='', rand=''):
    #     self.appid = appid
    #     self.SecretID = SecretID
    #     self.SecretKey = SecretKey
    #     self.bucket = bucket
    #     self.file = file
    #
    #     if currentTime == '':
    #         self.currentTime = int(time.time())
    #         self.expiredTime = self.currentTime + 60
    #         self.rand = random.randint(0, 9999999999)
    #     else:
    #         self.currentTime = currentTime
    #         self.expiredTime = expiredTime
    #         self.rand = rand
    #
    # def get_original(self):
    #     if self.file == '':
    #         t_tuple = (self.appid, self.bucket, self.SecretID, self.expiredTime, self.currentTime, self.rand)
    #         original = 'a=%s&b=%s&k=%s&e=%s&t=%s&r=%s&f=' % t_tuple
    #     else:
    #         t_tuple = (self.appid, self.bucket, self.file)
    #         filePath = '/%s/%s/%s' % t_tuple
    #         fileid = quote(filePath, safe='/', encoding='utf-8', errors=None)
    #         expired_time = 0
    #         t_tuple = (self.appid, self.bucket, self.SecretID, expired_time, self.currentTime, self.rand, fileid)
    #         original = 'a=%s&b=%s&k=%s&e=%s&t=%s&r=%s&f=%s' % t_tuple
    #
    #     return original
    #
    # def get_sign(self):
    #     original = self.get_original().encode('utf-8')
    #     secret_key = self.SecretKey.encode('utf-8')
    #     hmac_hexdigest = hmac.new(bytes(secret_key), bytes(original), hashlib.sha1).hexdigest()
    #     SignTmp = binascii.unhexlify(hmac_hexdigest)
    #     sign = base64.b64encode(SignTmp + original).decode('utf-8')
    #
    #     return sign
