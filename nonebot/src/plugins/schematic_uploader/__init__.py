import os
from httpx import AsyncClient

from nonebot import logger, on_shell_command
from nonebot.adapters.onebot.v11 import Bot, GroupMessageEvent
from nonebot.rule import ArgumentParser
from nonebot.typing import T_State

from . import config

schematic_command = config.schematic_command
schematic_folder = config.schematic_folder

parser = ArgumentParser(add_help=False)
action = parser.add_mutually_exclusive_group()
action.add_argument("-h", "--help", dest="help", action="store_true")
action.add_argument("-l", "--list", action="store_true")
action.add_argument("-u", "--upload", dest="ufilename")
action.add_argument("-d", "--delete", dest="dfilename")

sc = on_shell_command(schematic_command, parser=parser)

help_text = f"""原理图管理系统
-u | --upload <文件名(.schematic)>   上传原理图
-l | --list 列出所有原理图
-d | --delete <文件名(.schematic)>   删除原理图
/{schematic_command} [-u|-l|-d] [文件名]
"""


@sc.handle()
async def link(bot: Bot, event: GroupMessageEvent, state: T_State):
    args = vars(state.get("_args"))

    need_help = args.get('help')
    need_list = args.get('list')
    ufilename = args.get('ufilename', None)
    dfilename = args.get('dfilename', None)

    logger.debug(args)
    if need_help:
        await sc.finish(help_text)
    elif need_list:
        await sc.finish("\n".join([f for f in os.listdir(schematic_folder) if check_extension(f)]))
    elif ufilename is not None:
        await bot.send(event, "[schematic]处理中，请稍后…")
        filename: str = ufilename if check_extension(ufilename) else ufilename + ".schematic"
        root: dict = await bot.get_group_root_files(group_id=int(event.group_id))
        files: list = root.get('files')
        for folder in root.get('folders', []):
            file: dict = await bot.get_group_files_by_folder(group_id=int(event.group_id), folder_id=folder['folder_id'])
            files.extend(file.get('files'))

        searched_list: list[dict] = [i for i in files if filename == i['file_name']]

        if len(searched_list) == 0:
            await sc.finish("[schematic]未找到原理图文件")
        elif len(searched_list) > 1:
            await sc.finish("[schematic]存在重名文件，请修改文件名")
        elif len(searched_list) == 1:
            await sc.send("[schematic]已找到原理图，正在上传中...")
            file: dict = searched_list[0]
            url: str = await bot.get_group_file_url(group_id=int(event.group_id), file_id=file['file_id'], bus_id=file['busid']).get('url')
            async with AsyncClient() as client:
                response = await client.get(url)
                while check_dup(filename, schematic_folder):
                    filename = filename[:-10] + "_.schematic"
                with open(os.path.join(filename, schematic_folder), "wb") as f:
                    f.write(response.content)
            await sc.finish("[schematic]原理图上传完成!")
    elif dfilename is not None:
        await bot.send(event, "[schematic]处理中，请稍后…")
        filename: str = dfilename if check_extension(dfilename) else dfilename + ".schematic"
        if filename not in os.listdir(schematic_folder):
            await sc.finish("[schematic]未找到原理图文件")
        else:
            os.remove(os.path.join(filename, schematic_folder))
            await sc.finish("[schematic]原理图删除完成!")


def check_extension(filename: str):
    return filename[-10:] == ".schematic"


def check_dup(filename: str, dir_path: str):
    return filename in os.listdir(dir_path)
