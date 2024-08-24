import json
import re
import html

import nonebot
import requests
from nonebot import logger


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

    # @staticmethod
    # def for_qq(msg: str):
    #     at = re.compile("^\[CQ:at,qq=+\d+\]$")
    #     if re.search(at, msg) is not None:
    #         return "at", msg.replace("[CQ:at,qq=", "").replace("]", "")
    #     else:
    #         qq_result, qq_data = SQL.user_qq(msg)
    #         name_result, name_data = SQL.user_name(msg)
    #         if qq_result == 1 and qq_data:
    #             if name_result == 1 and name_data:
    #                 return "qq or name", msg + " " + qq_data[6] + " " + name_data[0] + " " + msg
    #             else:
    #                 return "qq", msg
    #         elif name_result == 1 and name_data:
    #             return "qq", name_data[0]
    #         else:
    #             return None, None
    # @staticmethod
    # def ip(text: str):
    #     find = re.findall(r'[0-9]+(?:\.[0-9]+){3}', text)
    #     for i in find:
    #         try:
    #             print("查询", i)
    #             result = requests.get(f"http://opendata.baidu.com/api.php?query={i}&co=&resource_id=6006&oe=utf8",
    #                                   timeout=5).json()
    #             print(result)
    #             text = re.sub(r'[0-9]+(?:\.[0-9]+){3}', "[IP:" +
    #                           result["data"][0]["location"] + "]", text, 1)
    #         except:
    #             continue
    #     return text
    @staticmethod
    def color(text: str):
        # \[i(tem)?(?:\/s(?<Stack>\d{1,3}))?(?:\/p(?<Prefix>\d{1,3}))?:(?<NetID>-?\d{1,4})\]
        # \[c(olor)?(\/(?<Color>[0-9a-fA-F]{6})):(?<Text>.*?)\]
        find = re.findall("\[c?\/[0-9a-fA-F]{6}:(.*?)\]", text)
        for i in find:
            text = re.sub("\[c?\/[0-9a-fA-F]{6}:(.*?)\]", i, text, 1)
        return text

    @staticmethod
    def item(text: str):
        with open("item.json", encoding='utf-8', errors='ignore') as fp:
            item_info = json.loads(fp.read())

        with open("prefix.json", encoding='utf-8', errors='ignore') as fp:
            prefix_info = json.loads(fp.read())
        find = re.findall("\[i?(?:\/s(\d{1,4}))?(?:\/p(\d{1,3}))?:(-?\d{1,4})\]", text)
        for i in find:
            try:
                item = "["
                item_id = int(i[2])
                num = i[0]
                prefix = i[1]
                if prefix != "":
                    prefix_index = int(prefix) - 1
                    item = item + prefix_info[prefix_index][1] + "的 "
                item = item + item_info[item_id-1][1]
                if num != "" and num != "1":
                    item = item + f"({num})"
                item = item + "]"
                text = re.sub("\[i?(?:\/s(\d{1,4}))?(?:\/p(\d{1,3}))?:(-?\d{1,4})\]", item, text, 1)
            except IndexError:
                logger.error("错误物品ID:"+str(item_id))

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