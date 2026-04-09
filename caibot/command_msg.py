from nonebot.adapters.milky import MessageSegment


class CommandMsg:
    def __init__(self, user_id: int | None, title: str, sub_title: str | None = None, success_msg: str | None = None,
                 failed_msg: str | None = None, syntax: str | None = None):
        self._user_id: int | None = user_id
        self._title: str = title
        self._success_msg: str | None = success_msg
        self._failed_msg: str | None = failed_msg
        self.sub_title: str | None = sub_title
        self._syntax: str | None = syntax

    def _get_base_msg(self) -> MessageSegment:
        msg = MessageSegment.text("")
        if self._user_id:
            msg += MessageSegment.mention(self._user_id)
            msg += MessageSegment.text("\n")

        if self.sub_title:
            msg += MessageSegment.text(f"『{self._title} • {self.sub_title}』\n")
        else:
            msg += MessageSegment.text(f"『{self._title}』\n")

        return msg

    def syntax_error(self) -> MessageSegment:
        msg = self._get_base_msg()
        msg += MessageSegment.text("格式错误！" + "\n")
        if self._syntax:
            msg += MessageSegment.text("正确格式: " + self._syntax)
        return msg

    def permission_denied(self) -> MessageSegment:
        msg = self._get_base_msg()
        msg += MessageSegment.text("没有权限！")
        return msg

    def success(self, result: str | MessageSegment | None) -> MessageSegment:
        msg = self._get_base_msg()
        if self._success_msg:
            msg += MessageSegment.text(self._success_msg + "\n")
        if result:
            if isinstance(result, MessageSegment):
                msg += result
            else:
                msg += MessageSegment.text(result)

        return msg

    def failed(self, reason: str | MessageSegment | None) -> MessageSegment:
        msg = self._get_base_msg()
        if self._failed_msg:
            msg += MessageSegment.text(self._failed_msg + "\n")
        if reason:
            if isinstance(reason, MessageSegment):
                msg += reason
            else:
                msg += MessageSegment.text(reason)

        return msg
