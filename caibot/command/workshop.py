import base64
import hashlib
import tempfile
import time
from pathlib import Path
from typing import Any

import httpx
from nonebot import on_command
from nonebot.adapters.milky import Bot
from nonebot.adapters.milky.event import GroupMessageEvent, MessageEvent

from caibot import CommandMsg
from caibot.dependency import Args
from caibot.downloader_api import (
    get_download_url,
    get_mod_files,
    get_mod_versions,
    submit_download,
)
from caibot.steamapi import SteamAPI

PAGE_SIZE = 5

_CACHE_DIR = Path(tempfile.gettempdir()) / "caibot_file_cache"
_CACHE_TTL = 86400


def _cache_path(file_url: str, file_name: str) -> Path:
    url_hash = hashlib.sha256(file_url.encode()).hexdigest()[:16]
    return _CACHE_DIR / url_hash / file_name


def _is_cache_valid(path: Path) -> bool:
    return path.exists() and (time.time() - path.stat().st_mtime) < _CACHE_TTL


def _cleanup_cache() -> None:
    if not _CACHE_DIR.exists():
        return
    now = time.time()
    for file in _CACHE_DIR.rglob("*"):
        if file.is_file() and (now - file.stat().st_mtime) >= _CACHE_TTL:
            file.unlink(missing_ok=True)
    for directory in sorted(_CACHE_DIR.rglob("*"), reverse=True):
        if directory.is_dir():
            try:
                directory.rmdir()
            except OSError:
                pass


_cleanup_cache()

search_mod = on_command("搜模组", force_whitespace=True, aliases={"搜mod", "搜MOD"})


@search_mod.handle()
async def _(event: MessageEvent, args: Args):
    msg = CommandMsg(
        user_id=event.data.sender.user_id if isinstance(event, GroupMessageEvent) else None,
        title="搜模组",
        syntax="搜模组 <关键词> [页码]"
    )

    if len(args) == 0:
        await search_mod.finish(msg.syntax_error())

    page = 1
    if len(args) >= 2 and args[-1].isdigit() and int(args[-1]) >= 1:
        page = int(args[-1])
        search_text = " ".join(args[:-1])
    else:
        search_text = " ".join(args)

    try:
        result = await SteamAPI.query_mods(search_text)
    except Exception as e:
        await search_mod.finish(msg.failed(f"搜索失败: {e}"))
        return

    if not result.publishedfiledetails:
        await search_mod.finish(msg.failed(f"未找到与「{search_text}」相关的Mod"))

    total_items = len(result.publishedfiledetails)
    total_pages = (total_items + PAGE_SIZE - 1) // PAGE_SIZE

    page = min(page, total_pages)

    start = (page - 1) * PAGE_SIZE
    page_items = result.publishedfiledetails[start:start + PAGE_SIZE]

    lines: list[str] = []

    for mod in page_items:
        lines.append(
            f"「{mod.title}」\n"
            f"ID: {mod.publishedfileid}\n"
            f"作者: {mod.kvtags_dict.get('Author', '未知')}\n"
            f"订阅数: {mod.subscriptions}\n"
            f"版本: {mod.kvtags_dict.get('modloaderversion', '未知')}" +
            (f"\n前置: {mod.kvtags_dict['modreferences']}" if mod.kvtags_dict.get('modreferences') else "")
        )

    lines.append("* 使用\"下载 <ID>\"下载模组")
    lines.append(f"* 使用\"搜模组 {search_text} [页码]\"翻页")

    msg.sub_title = f"{page}/{total_pages}页"

    await search_mod.finish(msg.success("\n\n".join(lines)))


search_resource = on_command("搜资源包", force_whitespace=True)


@search_resource.handle()
async def _(event: MessageEvent, args: Args):
    msg = CommandMsg(
        user_id=event.data.sender.user_id if isinstance(event, GroupMessageEvent) else None,
        title="搜资源包",
        syntax="搜资源包 <关键词> [页码]"
    )

    if len(args) == 0:
        await search_resource.finish(msg.syntax_error())

    # 检测末尾是否为页码
    page = 1
    if len(args) >= 2 and args[-1].isdigit() and int(args[-1]) >= 1:
        page = int(args[-1])
        search_text = " ".join(args[:-1])
    else:
        search_text = " ".join(args)

    try:
        result = await SteamAPI.query_resource(search_text)
    except Exception as e:
        await search_resource.finish(msg.failed(f"搜索失败: {e}"))
        return

    if not result.publishedfiledetails:
        await search_resource.finish(msg.failed(f"未找到与「{search_text}」相关的资源包"))

    total_items = len(result.publishedfiledetails)
    total_pages = (total_items + PAGE_SIZE - 1) // PAGE_SIZE

    page = min(page, total_pages)

    start = (page - 1) * PAGE_SIZE
    page_items = result.publishedfiledetails[start:start + PAGE_SIZE]

    lines: list[str] = []

    for package in page_items:
        lines.append(
            f"「{package.title}」\n"
            f"ID: {package.publishedfileid}\n"
            f"订阅数: {package.subscriptions}"
        )

    msg.sub_title = f"第{page}/{total_pages}页"
    lines.append("* 使用\"下载 <ID>\"下载资源包")
    lines.append(f"* 使用\"搜资源包 {search_text} [页码]\"翻页")

    await search_resource.finish(msg.success("\n\n".join(lines)))


download_mod = on_command("下载", force_whitespace=True)


def _version_key(v: dict) -> tuple[int, int]:
    try:
        year, month = v["name"].split(".")
        return int(year), int(month)
    except (ValueError, IndexError):
        return 0, 0


async def _download_and_upload(
        bot: Bot,
        event: MessageEvent,
        file_url: str,
        file_name: str,
) -> None:
    cached = _cache_path(file_url, file_name)
    if _is_cache_valid(cached):
        if isinstance(event, GroupMessageEvent):
            assert event.data.group is not None
            await bot.send_group_message_reaction(
                group_id=event.data.group.group_id,
                message_seq=event.message_id,
                reaction_type="emoji",
                reaction="127881",
            )
        else:
            await bot.send_private_message(
                user_id=event.data.sender.user_id,
                message="缓存命中，正在上传...",
            )
        file_bytes: bytes = cached.read_bytes()
    else:
        if isinstance(event, GroupMessageEvent):
            assert event.data.group is not None
            await bot.send_group_message_reaction(
                group_id=event.data.group.group_id,
                message_seq=event.message_id,
                reaction_type="emoji",
                reaction="128164",
            )
        else:
            await bot.send_private_message(
                user_id=event.data.sender.user_id,
                message="正在下载文件，请稍候...",
            )
        async with httpx.AsyncClient(timeout=120) as client:
            resp = await client.get(file_url)
            resp.raise_for_status()
            file_bytes = resp.content
        cached.parent.mkdir(parents=True, exist_ok=True)
        cached.write_bytes(file_bytes)

    file_b64 = base64.b64encode(file_bytes).decode()

    if isinstance(event, GroupMessageEvent):
        assert event.data.group is not None
        await bot.upload_group_file(
            group_id=event.data.group.group_id,
            base64=file_b64,
            file_name=file_name,
        )
    else:
        await bot.upload_private_file(
            user_id=event.data.sender.user_id,
            base64=file_b64,
            file_name=file_name,
        )


def _tshock_platform(asset_name: str) -> str:
    name = asset_name.removesuffix("-Release.zip")
    parts = name.split("-for-Terraria-", 1)
    if len(parts) == 2:
        rest = parts[1]
        idx = 0
        while idx < len(rest) and (rest[idx].isdigit() or rest[idx] == "."):
            idx += 1
        if idx < len(rest) and rest[idx] == "-":
            return rest[idx + 1:]
    return asset_name


@download_mod.handle()
async def _(bot: Bot, event: MessageEvent, args: Args):
    msg = CommandMsg(
        user_id=event.data.sender.user_id if isinstance(event, GroupMessageEvent) else None,
        title="下载",
        syntax="下载 <ID> [版本号]",
    )

    if len(args) == 0:
        await download_mod.finish(msg.syntax_error())

    mod_id: str = args[0]
    version: str | None = args[1] if len(args) >= 2 else None

    if mod_id.lower() == "tmodloader":
        try:
            await _download_and_upload(
                bot, event,
                "https://xget.xi-xu.me/gh/tModLoader/tModLoader/releases/latest/download/tModLoader.zip",
                "tModLoader.zip",
            )
        except Exception as e:
            await download_mod.finish(msg.failed(f"下载失败: {e}"))
        return

    if mod_id.lower() == "tshock":
        try:
            async with httpx.AsyncClient(timeout=30) as client:
                api_resp = await client.get(
                    "https://api.github.com/repos/Pryaxis/TShock/releases/latest",
                    headers={"Accept": "application/vnd.github+json"},
                )
                api_resp.raise_for_status()
                release_info = api_resp.json()
        except Exception as e:
            await download_mod.finish(msg.failed(f"获取TShock版本信息失败: {e}"))
            return

        zip_assets = [a for a in release_info["assets"] if a["name"].endswith(".zip")]
        if version is None:
            msg.sub_title = f"可用平台"
            lines = [f"• {_tshock_platform(a['name'])}" for a in zip_assets]
            lines.append(f"* 使用\"下载 tshock <平台>\"下载")
            await download_mod.finish(msg.success("\n".join(lines)))
            return

        matched_asset: dict[str, Any] | None = next(
            (a for a in zip_assets if version.lower() in a["name"].lower()), None
        )

        if matched_asset is None:
            await download_mod.finish(msg.failed(f"平台{version}不存在！"))
            return

        file_name = matched_asset["name"]
        file_url = f"https://xget.xi-xu.me/gh/Pryaxis/TShock/releases/latest/download/{file_name}"
        try:
            await _download_and_upload(bot, event, file_url, file_name)
        except Exception as e:
            await download_mod.finish(msg.failed(f"下载失败: {e}"))
        return

    if version is None:
        try:
            versions = await get_mod_versions(mod_id)
        except Exception as e:
            await download_mod.finish(msg.failed(f"查询失败: {e}"))
            return

        if versions is None:
            try:
                await submit_download(mod_id)
            except Exception as e:
                await download_mod.finish(msg.failed(f"提交下载失败: {e}"))
                return
            await download_mod.finish(msg.success("资源不存在，已提交到下载队列，请稍后重试"))
            return

        direct_zip = next(
            (v for v in versions if not v["isDirectory"] and v["name"].lower().endswith(".zip")),
            None,
        )
        if direct_zip is not None:
            file_url = get_download_url(mod_id, None, direct_zip["name"])
            try:
                await _download_and_upload(bot, event, file_url, direct_zip["name"])
            except Exception as e:
                await download_mod.finish(msg.failed(f"下载文件失败: {e}"))
            return

        filtered = [v for v in versions if not v["name"].endswith(".json")]
        filtered.sort(key=_version_key, reverse=True)
        msg.sub_title = "可用版本"
        lines = [f"• {v['name']}" for v in filtered]
        lines.append(f"* 使用\"下载 {mod_id} <版本号>\"指定版本")
        await download_mod.finish(msg.success("\n".join(lines)))
        return

    try:
        files = await get_mod_files(mod_id, version)
    except Exception as e:
        await download_mod.finish(msg.failed(f"查询失败: {e}"))
        return

    if files is None:
        await download_mod.finish(msg.failed(f"版本{version}不存在！"))
        return

    non_dir_files = [f for f in files if not f["isDirectory"]]
    zip_files = [f for f in non_dir_files if f["name"].lower().endswith(".zip")]

    if len(non_dir_files) == 1:
        target_file = non_dir_files[0]
    elif zip_files:
        target_file = zip_files[0]
    else:
        target_file = None

    if target_file is not None:
        file_url = get_download_url(mod_id, version, target_file["name"])
        try:
            await _download_and_upload(bot, event, file_url, target_file["name"])
        except Exception as e:
            await download_mod.finish(msg.failed(f"下载文件失败: {e}"))
