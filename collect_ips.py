import requests
from bs4 import BeautifulSoup
import re
import os
import ipaddress
from datetime import datetime

# ✅ URL 列表及简短名称
sources = {
    'https://api.uouin.com/cloudflare.html': 'uouin',
    'https://ip.164746.xyz': '164746',
    'https://raw.githubusercontent.com/ymyuuu/IPDB/main/BestCF/bestcfv4.txt': 'IPDB'
}

PORT = '443'  # 要追加的端口

# 正则
ipv4_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
ipv6_candidate_pattern = r'([a-fA-F0-9:]{2,39})'

headers = {
    'User-Agent': 'Mozilla/5.0'
}

if os.path.exists('ip.txt'):
    os.remove('ip.txt')

ip_dict = {}

# 格式：202506261145（年月日时分）
timestamp = datetime.now().strftime('%Y%m%d%H%M')

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

        for ip in re.findall(ipv4_pattern, text):
            try:
                if ipaddress.ip_address(ip).version == 4:
                    ip_with_port = f"{ip}:{PORT}"
                    ip_dict[ip_with_port] = f"{shortname}{timestamp}"
            except ValueError:
                continue

        for ip in re.findall(ipv6_candidate_pattern, text):
            try:
                ip_obj = ipaddress.ip_address(ip)
                if ip_obj.version == 6:
                    ip_with_port = f"[{ip_obj.compressed}]:{PORT}"
                    ip_dict[ip_with_port] = f"{shortname}{timestamp}"
            except ValueError:
                continue

    except requests.RequestException as e:
        print(f"[请求错误] {url} -> {e}")
    except Exception as e:
        print(f"[解析错误] {url} -> {e}")

# 写入精简格式文件
with open('ip.txt', 'w') as f:
    for ip in sorted(ip_dict, key=lambda x: (4 if '.' in x else 6, x)):
        f.write(f"{ip}#{ip_dict[ip]}\n")

print(f"✅ 成功采集 {len(ip_dict)} 个 IP，已写入 ip.txt（格式已精简）")
