# Bluelog@Mz1.version

> 此版本为Mz1在bluelog的基础上进行修改的版本。
>
> email: mzi_mzi@qq.com

## 准备的更新

1. 增加访问统计（log）原版本的log好像没有实装（基本功能实现）

   **备份模块中还需要增加log.db的备份**

2. ~~在settings中增加更换网站图标的功能(样式做了，功能没做)~~

3. ~~增加标题内容搜索功能~~【有了标题搜索和正文搜索，不过是分开的，暂时先这样了】

4. ~~增加admin统计页面做一点简单的数据分析~~【字数分类统计已经完成了，暂时先这样了】

5. ~~在写post的时候增加暂存/自动保存功能。~~【暂存功能基本完成，自动保存没做，暂时先这样了】

6. **增加音乐播放模块【有点想做成一个电台功能啊，但是这样做感觉得先封装点爬虫模块了（爬点网易云外链什么的）】**

7. **增加post的属性，可以在首页隐藏什么的**

8. **定时备份功能（尚未）+打包下载备份功能（已完成）**

### 访问记录

bluelog/logs/log.db



## Deployment

### for release 正式环境

(反向代理啥的自己接一下，需要配置X-Real-Ip)

先生成数据库文件再初始化用户名密码，再启动(非正规，之后再修，勉强能用)：

```
$ flask initdb
$ flask init
Username: Mz1
Password:
Repeat for confirmation:
Initializing the database...
Creating the temporary administrator account...
Creating the default category...
Done.
$ export FLASK_ENV=production
$ flask run --host=0.0.0.0 --port=9999
```

如果之前进行过配置，可以直接通过run.sh启动。



### for debug 测试环境

参考下方生成fake data并运行的方式

```
$ flask forge
$ flask run
```







**以下是原项目的readme内容**

<hr />

*A blue blog.*

> Example application for *[Python Web Development with Flask](https://helloflask.com/en/book/1)* (《[Flask Web 开发实战](https://helloflask.com/book/1)》).

Demo: http://bluelog.helloflask.com

![Screenshot](https://helloflask.com/screenshots/bluelog.png)

## Installation

clone:
```
$ git clone https://github.com/greyli/bluelog.git
$ cd bluelog
```
create & activate virtual env then install dependency:

with venv/virtualenv + pip:
```
$ python -m venv env  # use `virtualenv env` for Python2, use `python3 ...` for Python3 on Linux & macOS
$ source env/bin/activate  # use `env\Scripts\activate` on Windows
$ pip install -r requirements.txt
```
or with Pipenv:
```
$ pipenv install --dev
$ pipenv shell
```
generate fake data then run:
```
$ flask forge
$ flask run
* Running on http://127.0.0.1:5000/
```

Test account:

* username: `admin`
* password: `helloflask`

## License

This project is licensed under the MIT License (see the
[LICENSE](LICENSE) file for details).