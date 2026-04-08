from typing import Annotated

from nonebot.adapters import Message
from nonebot.params import Depends, CommandArg


def split_args(msg: Message = CommandArg()) -> list[str]:
    return msg.extract_plain_text().strip().split()


Args = Annotated[list[str], Depends(split_args)]
