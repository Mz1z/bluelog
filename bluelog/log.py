'''
author: Mz1
用于日志记录的类
'''

import os 
import time


basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# 日志记录类
class MzLog():
	LOG_DB = os.path.join(basedir,'logs','log.db')

	# 初始化数据库
	@staticmethod
	def init_db():
		print("[init] log db path: " + MzLog.LOG_DB)
	
	# 记录访问
	# 参数:
	# 	文章id
	# 	ip
	# 	User-Agent
	@staticmethod
	def view_log(**argv):
		for arg in argv:  # debug
			print(f'{arg} -> {argv[arg]}')



# 测试
if __name__ == '__main__':
	MzLog.init_db()
	MzLog.view_log(event="test")