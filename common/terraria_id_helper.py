import json

from nonebot.log import logger

with open("terraria_id/Item_ID.json", encoding='utf-8', errors='ignore') as fp:
    items = json.loads(fp.read())

with open("terraria_id/Prefix_ID.json", encoding='utf-8', errors='ignore') as fp:
    prefixes = json.loads(fp.read())

with open("terraria_id/Project_ID.json", encoding='utf-8', errors='ignore') as fp:
    projects = json.loads(fp.read())

with open("terraria_id/NPC_ID.json", encoding='utf-8', errors='ignore') as fp:
    NPCs = json.loads(fp.read())

with open("terraria_id/Buff_ID.json", encoding='utf-8', errors='ignore') as fp:
    buffs = json.loads(fp.read())

logger.warning("[terraria_id]物品、前缀、生物、Buff、弹幕已缓存!")


def get_item_info_string(item):
    info = [f"物品名: {item['Name']}", f"ID: {item['ItemId']}", f"最大堆叠: {item['MaxStack']}"]

    if item['Damage'] != -1:
        info.append(f"伤害: {item['Damage']}")

    monetary_value = item['MonetaryValue']

    if any(value != 0 for value in monetary_value.values()):
        monetary_info = (f"钱币: {str(monetary_value['Platinum']) + '铂' if monetary_value['Platinum'] != 0 else ''}"
                         f"{str(monetary_value['Gold']) + '金' if monetary_value['Gold'] != 0 else ''}"
                         f"{str(monetary_value['Silver']) + '银' if monetary_value['Silver'] != 0 else ''}"
                         f"{str(monetary_value['Copper']) + '铜' if monetary_value['Copper'] != 0 else ''}")
        info.append(monetary_info)
    else:
        info.append("钱币: 无价")

    if item['Description'] != "":
        info.append(f"{item['Description']}", )
    return "\n".join(info)


def get_npc_info_string(item):
    info = [f"生物名: {item['Name']}", f"ID: {item['NpcId']}", f"生命值: {item['LifeMax']}"]

    if item['Damage'] != -1:
        info.append(f"伤害: {item['Damage']}")

    monetary_value = item['MonetaryValue']

    if any(value != 0 for value in monetary_value.values()):
        monetary_info = (f"钱币: {str(monetary_value['Platinum']) + '铂' if monetary_value['Platinum'] != 0 else ''}"
                         f"{str(monetary_value['Gold']) + '金' if monetary_value['Gold'] != 0 else ''}"
                         f"{str(monetary_value['Silver']) + '银' if monetary_value['Silver'] != 0 else ''}"
                         f"{str(monetary_value['Copper']) + '铜' if monetary_value['Copper'] != 0 else ''}")
        info.append(monetary_info)
    else:
        info.append("钱币: 无价")

    if item['Description'] != "":
        info.append(f"{item['Description']}")
    return "\n".join(info)


def get_project_info_string(item):
    info = [f"弹幕名: {item['Name']}", f"ID: {item['ProjId']}", f"AI类型: {item['AiStyle']}",
            f"友方: {item['Friendly']}"]
    return "\n".join(info)


def get_buff_info_string(item):
    info = [f"增益名: {item['Name']}", f"ID: {item['BuffId']}"]
    if item['Description'] != "":
        info.append(f"{item['Description']}")
    return "\n".join(info)


def get_prefix_info_string(item):
    info = [f"修饰语: {item['Name']}", f"ID: {item['PrefixId']}"]
    return "\n".join(info)


def GetItemByNameOrId(query):
    # 尝试将查询转换为整数以检查是否为ID
    try:
        query_id = int(query)
        for item in items:
            if item["ItemId"] == query_id:
                return get_item_info_string(item)
    except ValueError:
        pass

    # 如果查询不是有效的ID，则按名称匹配
    matching_items = [item for item in items if item["Name"].startswith(query)]

    if len(matching_items) == 1:
        return get_item_info_string(matching_items[0])
    elif len(matching_items) > 1:
        return "有多个匹配结果: " + ", ".join([f'{item["Name"]}({item["ItemId"]})' for item in matching_items])
    else:
        return "啥东西都没找到哦!"


def GetNpcByNameOrId(query):
    # 尝试将查询转换为整数以检查是否为ID
    try:
        query_id = int(query)
        for item in NPCs:
            if item["NpcId"] == query_id:
                return get_npc_info_string(item)
    except ValueError:
        pass

    # 如果查询不是有效的ID，则按名称匹配
    matching_items = [item for item in NPCs if item["Name"].startswith(query)]

    if len(matching_items) == 1:
        return get_npc_info_string(matching_items[0])
    elif len(matching_items) > 1:
        return "有多个匹配结果: " + ", ".join([f'{item["Name"]}({item["NpcId"]})' for item in matching_items])
    else:
        return "啥东西都没找到哦!"


def GetProjectByNameOrId(query):
    # 尝试将查询转换为整数以检查是否为ID
    try:
        query_id = int(query)
        for item in projects:
            if item["ProjId"] == query_id:
                return get_project_info_string(item)
    except ValueError:
        pass

    # 如果查询不是有效的ID，则按名称匹配
    matching_items = [item for item in projects if item["Name"].startswith(query)]

    if len(matching_items) == 1:
        return get_project_info_string(matching_items[0])
    elif len(matching_items) > 1:
        return "有多个匹配结果: " + ", ".join(
            [f'{item["Name"]}{"·友" if item["Friendly"] else "·敌"}({item["ProjId"]})' for item in matching_items])
    else:
        return "啥东西都没找到哦!"


def GetBuffByNameOrId(query):
    # 尝试将查询转换为整数以检查是否为ID
    try:
        query_id = int(query)
        for item in buffs:
            if item["BuffId"] == query_id:
                return get_buff_info_string(item)
    except ValueError:
        pass

    # 如果查询不是有效的ID，则按名称匹配
    matching_items = [item for item in buffs if item["Name"].startswith(query)]

    if len(matching_items) == 1:
        return get_buff_info_string(matching_items[0])
    elif len(matching_items) > 1:
        return "有多个匹配结果: " + ", ".join([f'{item["Name"]}({item["BuffId"]})' for item in matching_items])
    else:
        return "啥东西都没找到哦!"


def GetPrefixByNameOrId(query):
    # 尝试将查询转换为整数以检查是否为ID
    try:
        query_id = int(query)
        for item in prefixes:
            if item["PrefixId"] == query_id:
                return get_prefix_info_string(item)
    except ValueError:
        pass

    # 如果查询不是有效的ID，则按名称匹配
    matching_items = [item for item in prefixes if item["Name"].startswith(query)]

    if len(matching_items) == 1:
        return get_prefix_info_string(matching_items[0])
    elif len(matching_items) > 1:
        return "有多个匹配结果: " + ", ".join([f'{item["Name"]}({item["PrefixId"]})' for item in matching_items])
    else:
        return "啥东西都没找到哦!"
