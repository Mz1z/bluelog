import os
import zipfile


# 打包压缩函数
# 压缩uploads和data-dev.db
def backup_zip(upload_dir='../uploads',db_file='../data-dev.db', backup_file='bak.zip'):
	f = zipfile.ZipFile(backup_file, 'w')
	for item in os.listdir(upload_dir):
		if item == '.gitkeep':
			continue
		file_path = upload_dir + os.sep + item
		arcname = 'uploads' + os.sep + item
		f.write(file_path, arcname)
	f.write(db_file, 'data-dev.db')
	f.close()
	
if __name__ == '__main__':
	backup_zip()
