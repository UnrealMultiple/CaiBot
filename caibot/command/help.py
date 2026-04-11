from nonebot import on_command

from caibot import CommandMsg
from caibot.dependency import User, BotAdminPermission

_USER_HELP = """\
「基础」
关于 - 查看Bot信息
help - 显示帮助列表
「创意工坊」
搜模组 <关键词> [页码] - 搜索tMod信息
搜资源包  <关键词> [页码] - 搜索资源包信息
下载 <ID> [版本] - 下载资源包/tMod
「云黑查询」
云黑列表 [页码] - 查看全局云黑名单
云黑检测 <QQ/all> - 检测成员是否在云黑名单
云黑详细 <记录ID> - 查看云黑记录详细信息
「群管理员」
添加云黑 <QQ> <理由> - 向反馈群提交云黑申请
删除云黑 <QQ> - 删除本群对该用户的云黑记录
「群主」
添加管理 <QQ> - 将用户设为本群Bot管理员
删除管理 <QQ> - 移除用户的本群Bot管理员权限"""
_ADMIN_HELP = """
「审核」
审核列表 - 查看待审核云黑申请
云黑批准 <请求ID> - 批准云黑申请
云黑驳回 <请求ID> <理由> - 驳回云黑申请
「云黑记录管理」
群云黑列表 <群号> [页码] - 查看指定群的云黑名单
群云黑删除 <云黑ID> - 根据记录ID删除云黑
「用户/群封禁」
禁止用户 <QQ> <禁止|解禁> - 禁止/解禁用户使用Bot
禁止群 <群号> <禁止|解禁> - 禁止/解禁群使用Bot
「云黑添加封禁」
云黑封禁 <QQ> <禁止|解禁> - 禁止/解禁用户提交云黑申请
群云黑封禁 <群号> <禁止|解禁> - 禁止/解禁群提交云黑申请
「工具」
lookfor <QQ> - 查找用户所在的群"""
help_cmd = on_command("help", force_whitespace=True, aliases={"帮助"})


@help_cmd.handle()
async def _(user: User, permission: BotAdminPermission):
    content = _USER_HELP + (_ADMIN_HELP if permission else "")
    msg = CommandMsg(user_id=user.user_id, title="CaiBot命令帮助")
    await help_cmd.finish(msg.success(content))
