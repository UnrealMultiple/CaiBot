import html
import json
import re

from nonebot import logger

with open("terraria_id/Item_ID.json", encoding='utf-8', errors='ignore') as fp:
    item_info = json.loads(fp.read())

with open("terraria_id/Prefix_ID.json", encoding='utf-8', errors='ignore') as fp:
    prefix_info = json.loads(fp.read())

print("[TextHandle]物品、前缀已缓存!")


class TextHandle:
    @staticmethod
    def check_name(name: str):
        # Define the pattern: only Chinese characters, English letters, and numbers are allowed
        pattern = re.compile(r'^[\u4e00-\u9fa5a-zA-Z0-9]+$')

        # Check if the string matches the pattern
        if pattern.match(name):
            return True
        else:
            return False

    @staticmethod
    def color(text: str):
        find = re.findall("\[c?\/[0-9a-fA-F]{6}:(.*?)\]", text)
        for i in find:
            text = re.sub("\[c?\/[0-9a-fA-F]{6}:(.*?)\]", i, text, 1)
        return text

    @staticmethod
    def item(text: str):

        find = re.findall("\[i?(?:\/s(\d{1,4}))?(?:\/p(\d{1,3}))?:(-?\d{1,4})\]", text)
        for i in find:
            try:
                item = "["
                item_id = int(i[2])
                num = i[0]
                prefix = i[1]
                if prefix != "":
                    item = item + prefix_info[prefix + 1]['Name'] + "的 "
                item = item + item_info[item_id]['Name']
                if num != "" and num != "1":
                    item = item + f"({num})"
                item = item + "]"
                text = re.sub("\[i?(?:\/s(\d{1,4}))?(?:\/p(\d{1,3}))?:(-?\d{1,4})\]", item, text, 1)
            except IndexError:
                logger.error("错误物品ID:" + str(item_id))

        return text

    @staticmethod
    def all(text: str):
        return TextHandle.item(TextHandle.color(text))

    # @staticmethod
    # def at_to_name(text: str):
    #     print(text)
    #     find = re.findall("\[CQ:at,qq=+(\d+)\]", text)
    #     if not find:
    #         print(text)
    #         return text
    #     for i in find:
    #         result, data = SQL.user_qq(i)
    #         if result == 1 and data[6] is not None:
    #             text = re.sub("\[CQ:at,qq=+(\d+)\]", data[6], text, 1)
    #         else:
    #             text = re.sub("\[CQ:at,qq=+(\d+)\]", "[未知]", text, 1)
    #     return text

    @staticmethod
    def html_decode(text: str):
        return html.unescape(text)

    @staticmethod
    def add_line_break(text:str, n:int) -> str:
        lines = [text[i:i + n] for i in range(0, len(text), n)]
        return "\n".join(lines)
