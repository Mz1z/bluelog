import os
import zipfile

from io import BytesIO
from PIL import Image

import requests
import re
import json

from bluelog.log import MzLog

# 打包压缩函数
# 压缩uploads和data-dev.db和log.db
def backup_zip(upload_dir='../uploads',db_file='../data-dev.db', log_db_file=MzLog.LOG_DB, backup_file='bak.zip'):
	f = zipfile.ZipFile(backup_file, 'w')
	for item in os.listdir(upload_dir):
		if item == '.gitkeep':
			continue
		file_path = upload_dir + os.sep + item
		arcname = 'uploads' + os.sep + item
		f.write(file_path, arcname)
	f.write(db_file, 'data-dev.db')
	f.write(log_db_file, 'logs' + os.sep +'log.db')
	f.close()
	
# 压缩图片函数，减轻网络压力
def compress_image(infile, mb=500, step=10, quality=80):
	"""不改变图片尺寸压缩到指定大小
	:param infile: 压缩源文件
	:param mb: 压缩目标，KB
	:param step: 每次调整的压缩比率
	:param quality: 初始压缩比率
	:return: 压缩文件字节流
	"""
	o_size = os.path.getsize(infile) / 1024
	# print(f'  > 原始大小：{o_size}')
	if o_size <= mb:
		with open(infile, 'rb') as f:
			content = f.read()
		return content      # 大小满足要求，直接返回字节流
		
	im = Image.open(infile)
	im = im.convert("RGB")      # 兼容处理png和jpg
	
	while o_size > mb:
		out = BytesIO()
		im.save(out, format="JPEG", quality=quality)
		if quality - step < 0:
			break
		_imgbytes = out.getvalue()
		o_size = len(_imgbytes) / 1024
		out.close()   # 销毁对象
		# print(f'  > 压缩至大小：{o_size} quality: {quality}')
		quality -= step   # 质量递减
	return _imgbytes

# 利用https://www.ipshudi.com/的接口进行ip属地和rDNS查询
def ip2location(ip):
	url = f"https://www.ipshudi.com/{ip}.htm"
	headers = {
		"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.5735.199 Safari/537.36",
		"Referer": "https://www.ip138.com/",	
	}
	r = requests.get(url, headers=headers)
	location = re.findall('<td class="th">归属地</td>\s*<td>\s*<span>(.*?)</span', r.text)
	if len(location) == 0:
		print(r.text)
		return False
	location = location[0]
	location = re.sub("<a.*?>","",location)
	location = re.sub("</a>","",location)
	ret = location.strip() + " "
	runner = re.findall('<td class="th">运营商</td><td><span>(.*?)</span>', r.text)
	runner = "" if len(runner) == 0 else runner[0]
	ret += runner.strip() + " "
	rdns_url = f"https://rdnsdb.com/api/rdns/?callback=jQuery1111010121005909139513_1694431459034&ip={ip}&_=1694431459035"
	r = requests.get(rdns_url, headers=headers)
	rdns = json.loads(re.findall("\((.*?)\)", r.text)[0]) if len(re.findall("\((.*?)\)", r.text)) != 0 else {"status":False}
	if rdns['status'] == True:
		ret += rdns['data']['result']
	return ret
	
if __name__ == '__main__':
	backup_zip()
