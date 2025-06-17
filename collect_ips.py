import requests
from bs4 import BeautifulSoup
import re
import os

# 目标URL列表
urls = [
    'https://api.uouin.com/cloudflare.html', 
    'https://ip.164746.xyz', 
    'https://raw.githubusercontent.com/ymyuuu/IPDB/refs/heads/main/BestCF/bestcfv4.txt'
]

# 正则表达式用于匹配IP地址
ip_pattern = r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}'

# 检查ip.txt文件是否存在,如果存在则删除它
if os.path.exists('ip.txt'):
    os.remove('ip.txt')

# 创建一个集合来存储唯一的IP地址
ip_set = set()

# 遍历每个URL
for url in urls:
    try:
        # 发送HTTP请求获取网页内容
        response = requests.get(url)
        response.raise_for_status()  # 检查请求是否成功
        
        # 根据URL判断内容类型
        if url == 'https://raw.githubusercontent.com/ymyuuu/IPDB/refs/heads/main/BestCF/bestcfv4.txt':
            # 直接处理文本内容
            ip_matches = re.findall(ip_pattern, response.text)
            ip_set.update(ip_matches)
        else:
            # 使用BeautifulSoup解析HTML
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # 根据网站的不同结构找到包含IP地址的元素
            if url == 'https://api.uouin.com/cloudflare.html':
                elements = soup.find_all('tr')
            elif url == 'https://ip.164746.xyz':
                elements = soup.find_all('tr')
            else:
                elements = soup.find_all('li')
            
            # 遍历所有元素,查找IP地址
            for element in elements:
                element_text = element.get_text()
                ip_matches = re.findall(ip_pattern, element_text)
                
                # 将找到的IP地址添加到集合中
                ip_set.update(ip_matches)

    except requests.RequestException as e:
        print(f"请求错误: {e}")
    except Exception as e:
        print(f"解析错误: {e}")

# 将唯一的IP地址写入文件
with open('ip.txt', 'w') as file:
    for ip in ip_set:
        file.write(ip + '
')

print('IP地址已保存到ip.txt文件中。')
