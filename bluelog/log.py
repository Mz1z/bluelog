'''
author: Mz1
用于日志记录的类
'''

import os 
import time


basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# 日志记录类
class MzLog():
	LOG_DB = os.path.join(basedir, 'log.db')
	
	# 记录访问
	@staticmethod
	def view_log():
		pass
