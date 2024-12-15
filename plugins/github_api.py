import asyncio
import base64
import datetime

import aiohttp
import nonebot
from fastapi import Request

import plugins.cai_api
from common.global_const import TSHOCK_GROUP, FEEDBACK_GROUP
from common.group_helper import GroupHelper

app = plugins.cai_api.app

star_user = []
@app.post("/plugins/github/")
async def handle_github_push(request: Request):
    payload = await request.json()
    event_type = request.headers.get("X-GitHub-Event")

    cst = datetime.timezone(datetime.timedelta(hours=8))  # 定义 CST 时区
    current_time = datetime.datetime.now(cst).strftime('%H:%M:%S')
    if event_type == "push":
        if "refs/tags/" in payload['ref']:
            return {"message": "阻止Tag推送..."}
        if payload['head_commit'] is None:
            return {"message": "阻止空提交推送..."}
        commits_message = ""
        for i in payload['commits']:
            commits_message += f"#️⃣ ({i['id'][:7]}) {i['message']} (by {i['author']['username']})\n"
        push_message = (f"⬆️ 新提交 {payload['repository']['full_name']} [{payload['ref'].split('/')[-1]}]\n"
                        f"by {payload['head_commit']['author']['name']}({payload['head_commit']['author']['username']}) | CST {current_time}\n\n"
                        f"{commits_message}\n"
                        f"查看差异 > {payload['compare']}")
        if payload['repository']['name'] == "TShockPlugin":
            await GroupHelper.send_group(TSHOCK_GROUP, push_message)
        if payload['repository']['name'] == "CaiBot":
            await GroupHelper.send_group(FEEDBACK_GROUP, push_message)
        return {"message": "推送成功!"}

    if event_type == "ping":
        return {"message": "pong"}
    if event_type == "star":
        if payload['action'] == "created":
            if payload['sender']['login'] + payload['repository']['full_name'] not in star_user:
                star_user.append(payload['sender']['login'] + payload['repository']['full_name'])
                star_message = (
                    f"🔭 新Star {payload['repository']['full_name']} [{payload['repository']['default_branch']}]\n"
                    f"by {payload['sender']['login']} | CST {current_time}\n"
                    f"✨ 当前仓库共有{payload['repository']['stargazers_count']}颗星星")
                if payload['repository']['name'] == "TShockPlugin":
                    await GroupHelper.send_group(TSHOCK_GROUP, star_message)
                if payload['repository']['name'] == "CaiBot":
                    await GroupHelper.send_group(FEEDBACK_GROUP, star_message)
            return {"message": "推送成功！"}
    if event_type == "release":
        if payload['action'] == "edited":
            async def download_and_upload():
                root_file_data = await nonebot.get_bot().call_api("get_group_root_files", group_id=TSHOCK_GROUP)
                folder = next(filter(lambda x: x['folder_name'] == 'TShock仓库插件包', root_file_data['folders']))
                file_data = await nonebot.get_bot().call_api("get_group_files_by_folder", group_id=TSHOCK_GROUP,
                                                             folder_id=folder['folder_id'])
                files = [f for f in file_data['files'] if f['uploader'] == 2990574917]
                files.sort(key=lambda x: x['modify_time'], reverse=True)
                if len(files) >= 10:
                    files_to_delete = files[9:]
                    for file in files_to_delete:
                        await nonebot.get_bot().call_api("delete_group_file", group_id=TSHOCK_GROUP,
                                                         folder_id=folder['folder_id'],
                                                         file_id=file['file_id'], busid=file['busid'])

                for file in files:
                    if file['file_name'] == f"(v{datetime.datetime.now().strftime('%Y.%m.%d')})Plugins.zip":
                        await nonebot.get_bot().call_api("delete_group_file", group_id=TSHOCK_GROUP,
                                                         folder_id=folder['folder_id'],
                                                         file_id=file['file_id'], busid=file['busid'])

                async with aiohttp.ClientSession() as session:
                    async with session.get(
                            "https://gitee.com/kksjsj/TShockPlugin/releases/download/V1.0.0.0/Plugins.zip") as response:
                        file_data = await response.read()
                        base64_data = base64.b64encode(file_data).decode('utf-8')
                await nonebot.get_bot().call_api("upload_group_file", group_id=TSHOCK_GROUP,
                                                 folder_id=folder['folder_id'],
                                                 file=f"base64://{base64_data}",
                                                 name=f"(v{datetime.datetime.now().strftime('%Y.%m.%d')})Plugins.zip")
                print("插件包已推送！")
            asyncio.create_task(download_and_upload())
            return {"message": "插件包正在推送，请稍候！"}
    if event_type == "pull_request":
        if payload['action'] == "opened":
            pull_message = (
                f"↙️ 新拉取请求 {payload['repository']['full_name']} [{payload['repository']['default_branch']}]\n"
                f"by {payload['pull_request']['user']['login']} | CST {current_time}\n\n"
                f"#️⃣ {payload['pull_request']['title']}\n\n"
                f"查看详细 > {payload['pull_request']['html_url']}")
            if payload['repository']['name'] == "TShockPlugin":
                await GroupHelper.send_group(TSHOCK_GROUP, pull_message)
            if payload['repository']['name'] == "CaiBot":
                await GroupHelper.send_group(FEEDBACK_GROUP, pull_message)
            return {"message": "推送成功!"}
    if event_type == "issues":
        if payload['action'] == "opened":
            issues_message = (
                f"❓ 新议题 {payload['repository']['full_name']} [{payload['repository']['default_branch']}]\n"
                f"by {payload['issue']['user']['login']} | CST {current_time}\n\n"
                f"#️⃣ {payload['issue']['title']}\n\n"
                f"查看详细 > {payload['issue']['html_url']}")
            if payload['repository']['name'] == "TShockPlugin":
                await GroupHelper.send_group(TSHOCK_GROUP, issues_message)
            if payload['repository']['name'] == "CaiBot":
                await GroupHelper.send_group(FEEDBACK_GROUP, issues_message)
            return {"message": "推送成功!"}
    return {"message": "未处理"}

