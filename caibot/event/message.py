from nonebot import on_message
from nonebot.adapters.milky import Bot
from nonebot.adapters.milky.event import GroupMessageEvent

message = on_message()
@message.handle()
async def _(event: GroupMessageEvent, bot: Bot):
    # 喜多
    if event.data.sender.user_id == 3292922753:
        await bot.send_group_message_reaction(
            group_id=3292922753,
            message_seq=event.message_id,
            reaction="12951",
            reaction_type="emoji"
        )