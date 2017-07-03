## 启动solr

进入：`{solr}/examples/`目录

执行：`java -jar start.jar`

## 使用uwsgi启动django

关闭uwsgi：`pkill -9 uwsgi`

查看uwsgi进程： `ps -aux|grep uwsgi`

一键启动uwsgi：`knight@ubuntu:~/XMLY_0826_demo/XMLY_8_4_demo$ uwsgi --ini django_uwsgi.ini`

`django_uwsgi.ini` 是uwsgi的配置文件
`django_nginx.conf` 是nginx配置文件

## 环境要求

> note: xamdin 需要使用0.6版本，github源码安装

环境要求见`requirements/commont.txt`

大家在每次添加新包之后，**记得**加入到上面的`commont.txt`中

## git快速使用


```
Command line instructions


Git global setup(全局设置)

git config --global user.name "your name"
git config --global user.email "your emial"

Create a new repository(创建一个新的库)

git clone your_git_adds
cd test
touch README.md
git add README.md
git commit -m "add README"
git push -u origin master

Existing folder（上传没有初始化库的文件夹）

cd existing_folder
git init
git remote add origin your_git_adds
git add .
git commit
git push -u origin master

Existing Git repository（上传一个已经存在的库）

cd existing_repo
git remote add origin your_git_adds
git push -u origin --all
git push -u origin --tags
```

## 403问题解决

部署阶段nginx配置文件具有读写权限即可。保证django_nginx.conf配置中media和static配置路径的正确。
media和static路径对应于settings.py中MEDIA_ROOT和STATIC_ROOT的设置路径

---

分割线，以下是早期文件

---
# django+nginx+uwsgi 部署

自强学堂 Django 部署(Nginx) http://www.ziqiangxuetang.com/django/django-nginx-deploy.html

部署示例 https://github.com/sherlockzoom/testsite

> 上面是部署的一个示例


## 关于虚拟环境的使用

~~在项目目录下`himlaya_ENV`虚拟环境(**好处在于不用重复安装之前的包**)~~

+ 项目中所有设置python解释器的地方都设置为这个虚拟环境

## 文件上传注意事项

+ `.idea`下的文件不要上传


# ~~git使用参考~~

+ [git分支管理](http://www.liaoxuefeng.com/wiki/0013739516305929606dd18361248578c67b8067c8c017b000/0013743862006503a1c5bf5a783434581661a3cc2084efa000)
+ [创建与合并分支](http://www.liaoxuefeng.com/wiki/0013739516305929606dd18361248578c67b8067c8c017b000/001375840038939c291467cc7c747b1810aab2fb8863508000)
+ [解决冲突](http://www.liaoxuefeng.com/wiki/0013739516305929606dd18361248578c67b8067c8c017b000/001375840202368c74be33fbd884e71b570f2cc3c0d1dcf000)
+ [分支管理策略](http://www.liaoxuefeng.com/wiki/0013739516305929606dd18361248578c67b8067c8c017b000/0013758410364457b9e3d821f4244beb0fd69c61a185ae0000)
+ [Bug分支](http://www.liaoxuefeng.com/wiki/0013739516305929606dd18361248578c67b8067c8c017b000/00137602359178794d966923e5c4134bc8bf98dfb03aea3000)
+ [Feature分支](http://www.liaoxuefeng.com/wiki/0013739516305929606dd18361248578c67b8067c8c017b000/001376026233004c47f22a16d1f4fa289ce45f14bbc8f11000)
+ [多人协作](http://www.liaoxuefeng.com/wiki/0013739516305929606dd18361248578c67b8067c8c017b000/0013760174128707b935b0be6fc4fc6ace66c4f15618f8d000)

# postgresql 备份脚本


```
#! /bin/bash

date_str=$(date +%Y%m%d-%T)
export PGPASSWORD=123456 
sudo su postgres && pg_dump -U postgres -w xmlydb > /home/postgres/backups/database_$date_str.bak
```
