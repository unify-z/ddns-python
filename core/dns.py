from alibabacloud_alidns20150109.client import Client as Alidns20150109Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_alidns20150109 import models as alidns_20150109_models
import requests
class AliyunDNS:
    def __init__(self,access_key_id,access_key_secret):
        self.access_key_id = access_key_id
        self.access_key_secret = access_key_secret
        self.client = self.create_client()

    def create_client(self) -> Alidns20150109Client:
        """
        使用AK&SK初始化账号Client
        @return: Client
        @throws Exception
        """
        config = open_api_models.Config(
            access_key_id=self.access_key_id,
            access_key_secret=self.access_key_secret
        )
        config.endpoint = 'alidns.cn-hangzhou.aliyuncs.com'
        return Alidns20150109Client(config)
    def get_domain_records(self,domain_name: str):
        """
        获取指定域名的所有解析记录列表
        @param client:      客户端
        @param domain_name:  域名名称
        """
        req = alidns_20150109_models.DescribeDomainRecordsRequest(
            domain_name=domain_name
        )
        resp = self.client.describe_domain_records(req)
        return resp.to_map().get('body',{}).get('DomainRecords',{}).get('Record',[]) # type: ignore
    def get_domain_record_info(self, record_id: str):
        """
        获取单个解析记录信息
        @param client:     客户端
        @param record_id:   解析记录ID
        """
        req = alidns_20150109_models.DescribeDomainRecordInfoRequest(
            record_id=record_id
        )
        resp = self.client.describe_domain_record_info(req)
        return resp.to_map()
    def update_domain_record(self,record_id: str,rr: str,type: str,value:str):
        """
        更新域名解析记录
        :param record_id: str，要更新的域名解析记录的ID。
        :param rr: str，要更新的域名解析记录的主机记录。
        :param type: str，要更新的域名解析记录的类型，例如A、CNAME等。
        :param value: str，要更新的域名解析记录的值。
        """
        req = alidns_20150109_models.UpdateDomainRecordRequest(
            record_id=record_id,
            rr=rr,
            type=type,
            value=value
        )
        self.client.update_domain_record(req)
    def create_domain_record(self,domain_name: str,rr: str,type: str,value:str):
        """
        创建域名解析记录
        @param client:         客户端
        @param domain_name:     域名名称
        @param rr:              主机记录
        @param type:            记录类型(A/NS/MX/TXT/CNAME/SRV/AAAA/CAA/REDIRECT_URL/FORWARD_URL)
        """
        req = alidns_20150109_models.AddDomainRecordRequest(
            domain_name=domain_name,
            rr=rr,
            type=type,
            value=value
        )
        self.client.add_domain_record(req)
        
class CloudflareDns:
    def __init__(self,email,api_key):
        self.email = email
        self.api_key = api_key
        self.headers = {
            'X-Auth-Email': self.email,
            'X-Auth-Key': self.api_key,
        }
        self.url = 'https://api.cloudflare.com/client/v4'
    def get_all_domains(self):
        """
        获取账户下所有域名
        """
        resp = requests.get(
            f'{self.url}/zones',
            headers=self.headers
        )
        return resp.json()
    def create_domain_record(self,zone_id: str,rr: str,type: str,value:str):
        """
        创建域名解析记录
        :param zone_id: str，域名ID。
        :param rr: str，主机记录。
        :param type: str，记录类型(A/NS/MX/TXT/CNAME/SRV/AAAA/CAA/REDIRECT_URL/FORWARD_URL)
        :param value: str，记录值。
        """
        resp =  requests.post(
            f'{self.url}/zones/{zone_id}/dns_records',
            headers=self.headers,
            json={
                'type': type,
                'name': rr,
                'content': value,
                'ttl': 1,
                'proxied': False
            }
        )
        return resp.json()
    def update_domain_record(self,zone_id: str,record_id: str,rr: str,type: str,value:str):
        """
        更新域名解析记录
        :param zone_id: str，域名ID。
        :param record_id: str，解析记录ID。
        :param rr: str，主机记录。
        :param type: str，记录类型
        """
        resp = requests.patch(
            f'{self.url}/zones/{zone_id}/dns_records/{record_id}',
            headers=self.headers,
            json={
                'type': type,
                'name': rr,
                'content': value,
                'ttl': 60,
                'proxied': False
            }
        )
        return resp.json()
    def get_domain_record_info(self,record_id: str,zone_id: str):
        """
        获取域名解析记录信息
        :param record_id: 解析记录ID
        :param zone_id: 域名ID
        """
        resp = requests.get(
            self.url + f'/zones/{zone_id}/dns_records/{record_id}',
            headers=self.headers
        )
        return resp.json()
    def get_all_records(self,zone_id: str):
        """
        获取域名解析记录列表
        :param zone_id: 域名ID
        """
        resp = requests.get(
            self.url + f'/zones/{zone_id}/dns_records',
            headers=self.headers
        )
        return resp.json()
