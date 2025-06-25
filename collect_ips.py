import requests
from bs4 import BeautifulSoup
import re
import os
import ipaddress

# 目标URL列表
urls = [
    'https://api.uouin.com/cloudflare.html',
    'https://ip.164746.xyz',
    'https://raw.githubusercontent.com/ymyuuu/IPDB/main/BestCF/bestcfv4.txt',
    'https://raw.githubusercontent.com/ymyuuu/IPDB/main/BestCF/bestcfv6.txt'
]

# 正则表达式
ipv4_pattern = r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'
ipv6_pattern = r'\b(?:[A-Fa-f0-9]{1,4}:){2,7}[A-Fa-f0-9]{1,4}\b'

# 请求头
headers = {
    'User-Agent': 'Mozilla/5.0'
}

# 清除旧文件
if os.path.exists('ip.txt'):
    os.remove('ip.txt')

# 使用集合去重
ip_set = set()

# 遍历每个URL
for url in urls:
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        content = response.text

        if url.endswith('.txt'):
            all_matches = re.findall(ipv4_pattern, content) + re.findall(ipv6_pattern, content)
        else:
            soup = BeautifulSoup(content, 'html.parser')
            elements = soup.find_all('tr') or soup.find_all('li')
            text_content = '\n'.join(el.get_text() for el in elements)
            all_matches = re.findall(ipv4_pattern, text_content) + re.findall(ipv6_pattern, text_content)

        # 验证合法性
        for ip in all_matches:
            try:
                ipaddress.ip_address(ip)
                ip_set.add(ip)
            except ValueError:
                continue

    except requests.RequestException as e:
        print(f"[请求错误] {url} -> {e}")
    except Exception as e:
        print(f"[解析错误] {url} -> {e}")

# 写入文件（合并）
with open('ip.txt', 'w') as file:
    for ip in sorted(ip_set, key=lambda x: (ipaddress.ip_address(x).version, x)):
        file.write(ip + '\n')

print(f"✅ 共采集到 {len(ip_set)} 个唯一 IP（含 IPv4 与 IPv6），已写入 ip.txt。")
