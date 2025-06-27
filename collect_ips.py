import requests
from bs4 import BeautifulSoup
import re
import os
import ipaddress
from datetime import datetime, timedelta

# ✅ URL源与简称
sources = {
    'https://api.uouin.com/cloudflare.html': 'Uouin',
    'https://ip.164746.xyz': 'ZhiXuanWang',
    'https://raw.githubusercontent.com/ymyuuu/IPDB/main/BestCF/bestcfv4.txt': 'IPDB'
}

PORT = '443'  # 目标端口号

# 正则表达式
ipv4_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
ipv6_candidate_pattern = r'([a-fA-F0-9:]{2,39})'

headers = {
    'User-Agent': 'Mozilla/5.0'
}

# 删除旧文件
for file in ['ip.txt', 'ipv6.txt']:
    if os.path.exists(file):
        os.remove(file)

# IP 分类存储
ipv4_dict = {}
ipv6_dict = {}

# 当前时间
timestamp = datetime.now().strftime('%Y%m%d%H%M')
beijing_time = datetime.utcnow() + timedelta(hours=8)
now_str = beijing_time.strftime('%Y-%m-%d-%H-%M')

# 遍历来源
for url, shortname in sources.items():
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        content = response.text

        if url.endswith('.txt'):
            text = content
        else:
            soup = BeautifulSoup(content, 'html.parser')
            elements = soup.find_all('tr') or soup.find_all('li')
            text = '\n'.join(el.get_text() for el in elements)

        # IPv4 提取
        for ip in re.findall(ipv4_pattern, text):
            try:
                if ipaddress.ip_address(ip).version == 4:
                    ip_with_port = f"{ip}:{PORT}"
                    comment = f"{shortname}-{timestamp}"
                    ipv4_dict[ip_with_port] = comment
            except ValueError:
                continue

        # IPv6 提取
        for ip in re.findall(ipv6_candidate_pattern, text):
            try:
                ip_obj = ipaddress.ip_address(ip)
                if ip_obj.version == 6:
                    ip_with_port = f"[{ip_obj.compressed}]:{PORT}"
                    comment = f"IPv6{shortname}-{timestamp}"
                    ipv6_dict[ip_with_port] = comment
            except ValueError:
                continue

    except requests.RequestException as e:
        print(f"[请求错误] {url} -> {e}")
    except Exception as e:
        print(f"[解析错误] {url} -> {e}")

# 写入 ip.txt（仅IPv4）
with open('ip.txt', 'w') as f4:
    f4.write(f"127.0.0.1:1234#采集时间{now_str}\n")
    for ip in sorted(ipv4_dict):
        f4.write(f"{ip}#{ipv4_dict[ip]}\n")

# 写入 ipv6.txt（仅IPv6）
with open('ipv6.txt', 'w') as f6:
    f6.write(f"[::1]:1234#采集时间{now_str}\n")
    for ip in sorted(ipv6_dict):
        f6.write(f"{ip}#{ipv6_dict[ip]}\n")

print(f"✅ IPv4 写入 ip.txt，共 {len(ipv4_dict)} 个")
print(f"✅ IPv6 写入 ipv6.txt，共 {len(ipv6_dict)} 个")
