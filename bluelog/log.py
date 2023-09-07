'''
author: Mz1
用于日志记录的类
'''

import os 
import time
import sqlite3
import time


basedir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

# 日志记录类
class MzLog():
	LOG_DB = os.path.join(basedir,'logs','log.db')

	# 初始化数据库
	@staticmethod
	def init_db():
		print("[init] log db path: " + MzLog.LOG_DB)
		if os.path.exists(MzLog.LOG_DB):
			os.unlink(MzLog.LOG_DB)    # 删除旧数据库
		conn = sqlite3.connect(MzLog.LOG_DB)
		c = conn.cursor()
		c.execute('''
			CREATE TABLE `log`(
				log_id INTEGER PRIMARY KEY AUTOINCREMENT,
				user_agent TEXT,
				ip TEXT NOT NULL,
				post_id INTERGER NOT NULL,
				time INTERGER NOT NULL
			);
		''')
		conn.commit()
		conn.close()
	
	# 记录访问
	# 参数:
	# 	文章id
	# 	ip
	# 	User-Agent
	@staticmethod
	def view_log(**argv):
		for arg in argv:  # debug
			print(f'{arg} -> {argv[arg]}')
		ip = argv.get('ip')
		post_id = argv.get('post_id')
		user_agent = argv.get('user_agent')
		if ip is None or \
			post_id is None or \
			user_agent is None:
			return False
		# 记录数据
		conn = sqlite3.connect(MzLog.LOG_DB)
		c = conn.cursor()
		c.execute('''
			INSERT INTO `log`(user_agent, ip, post_id, time)
			VALUES (?,?,?,?);
		''', (user_agent, ip, post_id, int(time.time())))
		conn.commit()
		conn.close()
		return True



# 测试
if __name__ == '__main__':
	MzLog.init_db()
	# print(MzLog.view_log(ip='192.168.56.101', post_id=1, user_agent="Chrome"))