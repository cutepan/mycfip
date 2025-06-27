import requests
from bs4 import BeautifulSoup
import re
import os
import ipaddress
from datetime import datetime
from datetime import datetime, timedelta, timezone

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
if os.path.exists('ip.txt'):
    os.remove('ip.txt')

# IP => 备注
ip_dict = {}

# 当前时间（不带冒号和秒）
timestamp = datetime.now().strftime('%Y%m%d%H%M')

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
                    ip_dict[ip_with_port] = comment
            except ValueError:
                continue

        # IPv6 提取
        for ip in re.findall(ipv6_candidate_pattern, text):
            try:
                ip_obj = ipaddress.ip_address(ip)
                if ip_obj.version == 6:
                    ip_with_port = f"[{ip_obj.compressed}]:{PORT}"
                    comment = f"IPv6{shortname}-{timestamp}"
                    ip_dict[ip_with_port] = comment
            except ValueError:
                continue

    except requests.RequestException as e:
        print(f"[请求错误] {url} -> {e}")
    except Exception as e:
        print(f"[解析错误] {url} -> {e}")

# 写入 ip.txt
with open('ip.txt', 'w') as f:
    # 写入当前时间，格式可以根据需要调整
    beijing_time = datetime.utcnow() + timedelta(hours=8)
    now_str = beijing_time.strftime('%Y-%m-%d-%H-%M')
    f.write(f"127.0.0.1:1234#采集时间{now_str}\n")
    for ip in sorted(ip_dict, key=lambda x: (4 if '.' in x else 6, x)):
        f.write(f"{ip}#{ip_dict[ip]}\n")

print(f"✅ 共采集 {len(ip_dict)} 个 IP，IPv6 添加前缀标识，格式已统一输出到 ip.txt")
