import asyncio
import aiohttp
from .dns import AliyunDNS, CloudflareDns
from .config import Config
from loguru import logger
import time
import socket

async def get_public_ip(type: str = 'ipv4'):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.0.0 Safari/537.36'}
    if type == 'ipv4':
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get('https://4.ipw.cn') as resp:
                return (await resp.text()).strip()
    elif type == 'ipv6':
        s = socket.socket(socket.AF_INET6, socket.SOCK_DGRAM)
        s.connect(('240e:928:1400:105::b', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip

async def init():
    config = Config()
    match config.dns['type']:
        case 'aliyun':
            alidns = AliyunDNS(config.dns.get('aliyun_access_key'), config.dns.get('aliyun_access_secret'))
            all_records = alidns.get_domain_records(config.domain)  # type: ignore
            a_record_info = next((record for record in all_records if record.get('RR') == config.sub_domain and record.get('Type') == 'A'), None)
            
            if a_record_info is None:
                ip = await get_public_ip('ipv4')
                logger.info(f"域名{config.sub_domain}.{config.domain} A记录不存在, 正在创建记录 ip:{ip}")
                alidns.create_domain_record(config.domain, config.sub_domain, 'A', ip)  # type: ignore
            
            if config.enable_ipv6:
                aaaa_record_info = next((record for record in all_records if record.get('RR') == config.sub_domain and record.get('Type') == 'AAAA'), None)
                
                if aaaa_record_info is None:
                    ip = await get_public_ip(type='ipv6')
                    logger.info(f"域名{config.sub_domain}.{config.domain} AAAA记录不存在, 正在创建记录 ip:{ip}")
                    alidns.create_domain_record(config.domain, config.sub_domain, 'AAAA', ip)  # type: ignore
            all_records = alidns.get_domain_records(config.domain)  # type: ignore
            a_record_info = next((record for record in all_records if record.get('RR') == config.sub_domain and record.get('Type') == 'A'), None)
            aaaa_record_info = next((record for record in all_records if record.get('RR') == config.sub_domain and record.get('Type') == 'AAAA'), None)
            
            a_record_id = a_record_info['RecordId'] if a_record_info else None
            a_dns_ip = a_record_info['Value'] if a_record_info else None
            aaaa_record_id = aaaa_record_info['RecordId'] if aaaa_record_info else None
            aaaa_dns_ip = aaaa_record_info['Value'] if aaaa_record_info else None
            
            def update_domain_record(record_id, rr, type, value):  # type: ignore
                alidns.update_domain_record(record_id, rr, type, value)
        
        case 'cloudflare':
            cfdns = CloudflareDns(config.dns['email'], config.dns['api_key'])
            all_domains = cfdns.get_all_domains()
            zone_id = next((domain['id'] for domain in all_domains['result'] if domain['name'] == config.domain), None)  # 使用 next() 获取第一个匹配项
            
            all_records = cfdns.get_all_records(zone_id)
            a_record_info = next((record for record in all_records['result'] if record['type'] == 'A' and record['name'] == f"{config.sub_domain}.{config.domain}"), None)
            aaaa_record_info = next((record for record in all_records['result'] if record['type'] == 'AAAA' and record['name'] == f"{config.sub_domain}.{config.domain}"), None)
            
            if a_record_info is None:
                ip = await get_public_ip('ipv4')
                logger.info(f"域名 {config.sub_domain}.{config.domain} A 记录不存在, 正在创建记录 ip: {ip}")
                cfdns.create_domain_record(zone_id, config.sub_domain, 'A', ip)
            
            if config.enable_ipv6 and aaaa_record_info is None:
                ip = await get_public_ip(type='ipv6')
                logger.info(f"域名 {config.sub_domain}.{config.domain} AAAA 记录不存在, 正在创建记录 ip: {ip}")
                cfdns.create_domain_record(zone_id, config.sub_domain, 'AAAA', ip)
            
            a_dns_ip = a_record_info['content'] if a_record_info else None
            aaaa_dns_ip = aaaa_record_info['content'] if aaaa_record_info else None
            a_record_id = a_record_info['id'] if a_record_info else None
            aaaa_record_id = aaaa_record_info['id'] if aaaa_record_info else None
            
            def update_domain_record(record_id, rr, type, value):
                cfdns.update_domain_record(zone_id, record_id, rr, type, value)

    while True:
        a_pub_ip = await get_public_ip('ipv4')
        aaaa_pub_ip = await get_public_ip('ipv6') if config.enable_ipv6 else None
        
        if a_pub_ip != a_dns_ip:
            logger.info(f"IPv4 IP 已更新, 正在更新解析记录, 新 IP: {a_pub_ip}")
            update_domain_record(a_record_id, config.sub_domain, 'A', a_pub_ip)  # type: ignore
            a_dns_ip = a_pub_ip
        
        if config.enable_ipv6 and (aaaa_pub_ip != aaaa_dns_ip):
            logger.info(f"IPv6 IP 已更新, 正在更新解析记录, 新 IP: {aaaa_pub_ip}")
            update_domain_record(aaaa_record_id, config.sub_domain, 'AAAA', aaaa_pub_ip)  # type: ignore
            aaaa_dns_ip = aaaa_pub_ip
        
        logger.debug(f"IP 未更新 [time={time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}]")
        await asyncio.sleep(30)