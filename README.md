# tg-send-msg-exam-bot
Telegram 第一次发言 人机验证 机器人  
用户在群组中第一次发言时, 机器人会删除用户的消息, 并屏蔽用户发言权限.  
只有用户通过人机验证后, 才能恢复发言权限.

## 申请 bot_token

https://t.me/BotFather

/start

/newbot

提交 bot的name

提交 bot的username

得到 bot_token

<img width="562" height="366" alt="image" src="https://github.com/user-attachments/assets/39f63b51-75fc-4ee8-bddc-669fe015175d" />

## 部署

安装python  
一般你用的比较新版本的操作系统 Debian / Ubuntu, 已经自带了.   
略

安装 pip
```
apt install -y python3-pip
```

安装python依赖
```
pip3 install "python-telegram-bot[job-queue]" requests BeautifulSoup4 --break-system-packages
```

下载本项目代码
```
apt install -y git
git clone https://github.com/crazypeace/tg-send-msg-exam-bot.git
cd tg-send-msg-exam-bot
```

修改代码, 填写自己的 bot_token
<img width="1414" height="649" alt="image" src="https://github.com/user-attachments/assets/16b9277f-aca5-438c-b1eb-e014450fe27a" />

## 运行bot

```
python3 tg-send-msg-exam-bot.py
```

## 将bot添加到你的群
<img width="427" height="693" alt="image" src="https://github.com/user-attachments/assets/ccb1d3a7-92f8-4fca-a6fd-a9c0a9aca13e" />

## 将bot设置为管理员
<img width="540" height="386" alt="image" src="https://github.com/user-attachments/assets/b9e6a598-e6f3-4fb9-9e16-245325fc6b2a" />

## 部署完成
当有群成员发言时, 机器人就开始工作了.

# 自定义 问题-答案
在 pset 目录中, 各个 .py 文件定义了 问题-答案 的生成方法   
你可以删除你不需要的 问题-答案, 也可以很方便地自定义你自己的 问题-答案.

## youtube.py
如果是简单文本的 问题-答案, 可以参考 [youtube.py](https://github.com/crazypeace/tg-join-group-exam-bot/blob/main/pset/youtube.py) 文件.  
<img width="800" height="166" alt="image" src="https://github.com/user-attachments/assets/4ee17d64-e7e2-40d9-bd2b-ced7a4284946" />

## blog.py 
使用 [blog.py](https://github.com/crazypeace/tg-join-group-exam-bot/blob/main/pset/blog.py) 可以设置 "我的博客最新的一篇博文的标题是什么?" 这样的 问题-回答  
blog.py 也是一个例子, 用于在某个html页面上获取指定的元素作为答案.  
更详细的说明, 请见: https://zelikk.blogspot.com/2025/10/tg-antispam-bot-3.html  

## rss.py 
使用 [rss.py](https://github.com/crazypeace/tg-join-group-exam-bot/blob/main/pset/rss.py) 可以设置 "我的博客最新的一篇博文的标题是什么?" 这样的 问题-回答  
rss.py 也是一个例子, 用于在某个xml文件中获取指定元素作为答案.  
更详细的说明, 请见: https://zelikk.blogspot.com/2025/10/tg-antispam-bot-3.html  

# 保存消息并恢复
本项目可以实现这样的功能  
机器人 删除消息前, 将消息转发到 仓库频道 保存.  
当 用户 通过人机验证后, 机器人 从 仓库频道 将保存的消息转发到群组中.

新建一个频道, 设置机器人为频道的管理员.  

修改本程序, 设置 仓库频道的ID  
<img width="1388" height="459" alt="image" src="https://github.com/user-attachments/assets/6224fd2d-ebc1-4502-8fbc-62046d5f4392" />

