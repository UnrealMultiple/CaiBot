[staticmethod]
class sql_setting:
    type = "SQLite"  # MySQL / SQLite
    mysql_host = "wujiawei131108.mysql.rds.aliyuncs.com"
    mysql_port = 3306
    mysql_db = "bot"
    mysql_user = "terraria"
    mysql_passport = "Wujiawei131108"


class message_setting:
    multi_world = False  # 启用主城
    multi_world_ip = "🍵IP: terraria.ink\n" \
                      "🍵端口: 7777\n🍵TMODL端口: 12306"  # 启用主城后IP自定义提示
    help ="""萌新看这里(◦˙▽˙◦)""群内发送：
添加白名单 你的泰拉角色名字
即可添加白名单
举个栗子：添加白名单 沃尔特
第一次玩服务器的点开多人游戏，选择角色之后点开上面第二个，看到右下角添加，在群内发送ip即可获取服务器ip端口，输入之后就进入游戏让你输入的密码是你自己这个账号想设置什么密码，防止别人盗号，输入完之后就可以进入游戏啦(≧▽≦)
要创建房屋，请使用以下命令:
/house set 1 （设置房子左上角）
/house set 2 （设置房子右上角）
/house add 房屋名字
其他命令: list, allow, disallow, redefine, name, delete, clear, info, adduser, deluser, lock
/house allow 与其他玩家共享你的房屋权限
/house disallow 取消与其他玩家共享权限
剩下的我不知道(´•ω•̥`)
"""
    use_server_name = False  # 使用设置的服务器名称(速度快,看不见地图名字)
    use_online_progress = True  # 在线显示服务器进度




class api_setting:
    enabled = True
    host = "0.0.0.0"
    prot = 8037
    token = "wujiawei"  # 反向rest api密钥
    debug = True



class sync_message_setting:
    auto_to_server = True
    auto_to_bot = False
    send_group =[1134311185]

class perm_setting:
    to_two_perm_money = 8888


class sign_in_setting:
    max_money = 600
    min_money= 400

class general_setting:
    superadmin = ["3042538328","3082068984"]