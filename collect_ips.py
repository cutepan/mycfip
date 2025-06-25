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
ipv6_candidate_pattern = r'([a-fA-F0-9:]{2,39})'  # 宽松 IPv6 提取

# 请求头
headers = {
    'User-Agent': 'Mozilla/5.0'
}

# 清除旧文件
if os.path.exists('ip.txt'):
    os.remove('ip.txt')

ip_set = set()  # 存储 IPv4 + IPv6

# 遍历每个 URL
for url in urls:
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        content = response.text

        # 提取文本
        if url.endswith('.txt'):
            text = content
        else:
            soup = BeautifulSoup(content, 'html.parser')
            elements = soup.find_all('tr') or soup.find_all('li')
            text = '\n'.join(el.get_text() for el in elements)

        # 匹配 IPv4
        for ip in re.findall(ipv4_pattern, text):
            try:
                if ipaddress.ip_address(ip).version == 4:
                    ip_set.add(ip)
            except ValueError:
                continue

        # 匹配 IPv6（宽松匹配 + 验证合法性）
        for ip in re.findall(ipv6_candidate_pattern, text):
            try:
                ip_obj = ipaddress.ip_address(ip)
                if ip_obj.version == 6:
                    ip_set.add(str(ip_obj))  # 转成规范形式
            except ValueError:
                continue

    except requests.RequestException as e:
        print(f"[请求错误] {url} -> {e}")
    except Exception as e:
        print(f"[解析错误] {url} -> {e}")

# 写入合并文件 ip.txt
with open('ip.txt', 'w') as f:
    for ip in sorted(ip_set, key=lambda x: (ipaddress.ip_address(x).version, x)):
        f.write(ip + '\n')

print(f"✅ 采集完成，共 {len(ip_set)} 个唯一 IP（IPv4 + IPv6），已写入 ip.txt。")
