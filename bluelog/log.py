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

	# 获取单个文章的访问次数
	@staticmethod
	def get_post_view_count(post_id):
		conn = sqlite3.connect(MzLog.LOG_DB)
		c = conn.cursor()
		c.execute('''
			SELECT count(*) FROM log WHERE post_id=?;
		''', (post_id, ))
		ret = c.fetchone()[0]
		conn.close()
		return ret

	# 获取全部文章的访问次数
	@staticmethod
	def get_all_view_count():
		conn = sqlite3.connect(MzLog.LOG_DB)
		c = conn.cursor()
		c.execute('''
			SELECT count(*) FROM log;
		''')
		ret = c.fetchone()[0]
		conn.close()
		return ret

	# 获取最近访问的n条数据
	@staticmethod
	def get_records(n=5, offset=0):
		conn = sqlite3.connect(MzLog.LOG_DB)
		c = conn.cursor()
		rows = c.execute('''
			SELECT log_id, ip, user_agent, post_id, datetime(time,'unixepoch','localtime') FROM log ORDER BY time DESC LIMIT ? OFFSET ?;
		''', (n, offset))
		ret = []
		for row in rows:
			ret.append(row)
		conn.close()
		return ret

# 测试
if __name__ == '__main__':
	# MzLog.init_db()
	# print(MzLog.view_log(ip='192.168.56.101', post_id=1, user_agent="Chrome"))
	print(MzLog.get_post_view_count(60))
	print(MzLog.get_all_view_count())
	print(MzLog.get_records())