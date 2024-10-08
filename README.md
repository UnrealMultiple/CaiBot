![CaiBotDocument](https://socialify.git.ci/UnrealMultiple/CaiBot/image?font=Inter&forks=1&issues=1&language=1&logo=https%3A%2F%2Fq.qlogo.cn%2Fheadimg_dl%3Fdst_uin%3D2990574917%26spec%3D640%26img_type%3Dpng&name=1&owner=1&pattern=Circuit%20Board&pulls=1&stargazers=1&theme=Auto)

# 📄关于CaiBot

- 由于目前Cai还没有`企业资格`，所以暂时`用不了官方BOT接口`
- CaiBot是`为Terraria而开发`的，请不要把她拉进`非Terraria相关`的群
- 如果你想要Cai添加某些实用功能，可以发`Issue`提出意见
- 当然有bug你也可以在`Issue`中反馈

---

# 💾关于本仓库

### 前言

- 此仓库用于BOT代码管理维护
- 任何人都可以通过PR提交
- BOT将会自动从仓库拉取代码
- 插件在TShockPlugins仓库中...

### 开发者注意事项

- 字段、方法命名规范
- 长IO操作均需要使用异步

### 依赖 (大概吧)

~~~
pip install nb-cli,nonebot2,nonebot2[fastapi],nonebot-adapter-onebot,pymysql
pip install pillow==9.5.0
~~~
---

# 📖“部署”教程

1. 添加CaiBot的QQ`2990574917`
2. 发送加群邀请  
3. 群内发送`启用云黑` (如果你只想用云黑功能就到此为止)  
4. 群内发送`启用群机器人`  
5. 在群内发送`菜单`，并在菜单中找到适配插件/MOD下载地址  
6. 安装适配插件/MOD
7. 启动服务器，并记下`绑定码`  
8. 群内发送`添加服务器 <IP地址> <端口> <验证码>`  
9. 绑定服务器完成!发送`菜单`查看详细功能，发送`在线`查看服务器连接情况  
> [!CAUTION]
> 你可以在`tshock/CaiBot.json`中关闭`CaiBot的白名单`功能

---

# 🔍命令列表

| 命令(别名)             |         功能         |                格式                 |
|--------------------|:------------------:|:---------------------------------:|
| 关于                 |   查看CaiBot的信息和状态   |                 无                 |
| 云黑帮助               |      查看云黑帮助清单      |                 无                 |
| 菜单                 |     查看服务器相关功能      |                 无                 |
| 云黑检测               |    检查用户是否在云黑名单中    |     云黑检测 <QQ号> [all/*表示全群检测]      |
| 云黑详细               |     查看云黑的详细信息      |  云黑详细 <QQ号> [包含群号、添加者] (需要管理员权限)  |
| 随机云黑               |      随机查看一个云黑      |                 无                 |
| 云黑列表               | 查看CaiBOT储存的所有云黑记录  |             云黑列表 <页码>             |
| 添加云黑               |       添加一个云黑       |     添加云黑 <QQ号> <理由> (需要管理员权限)     |
| 删除云黑               |       删除一个云黑       |       删除云黑 <QQ号> (需要管理员权限)        |
| 添加管理 (云黑管理添加，管理添加) |    添加一个CaiBot管理    |        添加管理 <QQ号> (需要群主权限)        |
| 删除管理 (云黑管理删除，管理删除) |    删除一个CaiBot管理    |        删除管理 <QQ号> (需要群主权限)        |
| 启用群机器人             | 启用CaiBot的服务器机器人功能  |            无 (需要管理员权限)            |
| 关闭群机器人             | 关闭CaiBot的服务器机器人功能  |            无 (需要管理员权限)            |
| 添加服务器              |      绑定一台服务器       | 添加服务器 <IP地址> <端口> <验证码> (需要管理员权限) |
| 删除服务器              |      删除一台服务器       |      删除服务器 <服务器序号> (需要管理员权限)      |
| 在线                 |     获取服务器在线列表      |                 无                 |
| 远程指令               | 让指定服务器以超级管理员身份允许命令 |   远程指令 <服务器序号> <命令内容> (需要管理员权限)   |
| 查绑定                |    查询一个玩家的绑定信息     |          查绑定 <玩家名/玩家QQ>           |
| 查看地图               |      获取地图图片]       |      查看地图 <服务器序号> (需要管理员权限)       |
| wiki <搜索内容>        |      查询泰拉瑞亚百科      |                 无                 |
| 签到                 |       签到获取金币       |                 无                 |
| 自踢 (自提)            |      将你踢出服务器       |                 无                 |
| 进度查询 <服务器序号>       |     查询服务器的进度信息     |           进度查询 <服务器序号>            |
| 查背包                |   查询服务器中某名玩家的背包    |         查背包 <服务器序号> <玩家名>         |
| 清空设备               |    清空发送者绑定的所有设备    |               清空设备                |
| 登录                 |  同意CaiBot白名单登录请求   |                 无                 |
| 拒绝                 |  拒绝CaiBot白名单登录请求   |                 无                 |
| 添加白名单              |    绑定你的角色到小小Cai    |            添加白名单 <名字>             |
| 修改白名单              |       重新绑定角色       |            修改白名单 <名字>             |
> [!NOTE]
> 发送`菜单`查看所有命令
---

# 🧪TShock中文插件收集仓库

- [Controllerdestiny/TShockPlugin](https://github.com/Controllerdestiny/TShockPlugin)

# 🧰TShock插件开发文档

- [ACaiCat/TShockPluginDocument](https://github.com/ACaiCat/TShockPluginDocument)


