import time
import json
from multiprocessing import Process

from PIL import Image, ImageChops, ImageDraw, ImageFont


def get_bag_png(name: str, inv, buffs):
    font = "font/LXGWWenKaiMonoGB-Bold.ttf"
    img = Image.open("img/Cai.png").convert('RGBA')

    ft = ImageFont.truetype(font=font, size=100)

    w, h = img.size
    text_w, text_h = ft.getsize(name)
    draw = ImageDraw.Draw(img)
    draw.text(((w - text_w) / 2, 0), name, font=ft)

    ft = ImageFont.truetype(font=font, size=60)
    draw = ImageDraw.Draw(img)
    size = 25

    def draw_item(x: int, y: int, id: int, stack: int):
        try:
            # item = Image.open(f"img/Item/Item_{id}.png").convert('RGBA')
            # r, g, b, aitem = item.split()
            # img.paste(item, (round((x)), round((y))),mask=aitem)

            # ft = ImageFont.truetype(font=font, size=15)
            # draw.text((x,y),str(stack),font=ft)
            item = Image.open(f"img/Item/Item_{id}.png").convert("RGBA")

            original_image = item
            width, height = original_image.size

            # 计算新的宽度和高度，保持原有的比例
            if width > height:
                new_height = int(height * size / width)
                new_width = size
            else:
                new_width = int(width * size / height)
                new_height = size

            item = original_image.resize((new_width, new_height))

            ft = ImageFont.truetype(font="font/LXGWWenKaiMonoGB-Bold.ttf", size=14)

            r, g, b, a = item.split()
            img.paste(item, (x + 13, y + 13), mask=a)
            if stack != 1 and stack != 0:
                draw.text((x + 6, y + 30), str(stack), font=ft)
        except:
            pass

    def draw_buff(x: int, y: int, id: int):
        try:
            if id == 0:
                return
            buff = Image.open(f"img/buff/buff_{id}.png").convert("RGBA")
            _, _, _, a2 = buff.split()

            img.paste(buff, (x, y), mask=a2)
        except:
            pass

    back3 = Image.open("img/Item/Inventory_Back7.png").convert('RGBA')
    back4 = Image.open("img/Item/Inventory_Back8.png").convert('RGBA')
    back5 = Image.open("img/Item/Inventory_Back3.png").convert('RGBA')
    back1 = Image.open("img/Item/Inventory_Back.png").convert('RGBA')
    back6 = Image.open("img/Item/Inventory_Back12.png").convert('RGBA')
    r, g, b, a1 = back1.split()

    for h in range(5):
        for i in range(10):
            img.paste(back1, (150 + i * back1.width, back1.height * h + 120), mask=a1)  # 背包
    index = 0
    for h in range(5):
        for i in range(10):
            draw_item(150 + i * back1.width, back1.height * h + 120, inv[index][0], inv[index][1])
            index += 1

    Satchel = Image.open("img/Item/item_5343.png").convert('RGBA')
    Satchel = Satchel.resize((48, 32), Image.LANCZOS)
    r, g, b, aSatchel = Satchel.split()
    img.paste(Satchel, (150 - 50, Satchel.height * 3 + 35), mask=aSatchel)

    back2 = Image.open("img/Item/Inventory_Back11.png").convert('RGBA')
    r, g, b, a = back2.split()
    for h in range(4):
        for i in range(10):
            img.paste(back2, (740 + i * back2.width, back2.height * h + 120), mask=a)  # 猪猪
    index = 99

    for h in range(4):
        for i in range(10):
            draw_item(740 + i * back2.width, back2.height * h + 120, inv[index][0], inv[index][1])
            index += 1
    pig = Image.open("img/Item/item_87.png").convert('RGBA')
    pig = pig.resize((48, 32), Image.LANCZOS)
    r, g, b, apig = pig.split()
    img.paste(pig, (740 - 50, back2.height * 2 + 25), mask=apig)
    for h in range(4):
        for i in range(10):
            img.paste(back2, (1330 + i * back2.width, back2.height * h + 120), mask=a)  # 保险
    for h in range(4):
        for i in range(10):
            draw_item(1330 + i * back2.width, back2.height * h + 120, inv[index][0], inv[index][1])
            index += 1
    safe = Image.open("img/Item/item_346.png").convert('RGBA')
    safe = safe.resize((48, 48), Image.LANCZOS)
    r, g, b, asafe = safe.split()
    img.paste(safe, (1330 - 50, back2.height * 2 + 21), mask=asafe)

    index += 1

    for h in range(4):
        for i in range(10):
            img.paste(back2, (1330 + i * back2.width, back2.height * h + 120 + 280), mask=a)  # 熔炉
    for h in range(4):
        for i in range(10):
            draw_item(1330 + i * back2.width, back2.height * h + 120 + 280, inv[index][0], inv[index][1])
            index += 1
    Forge = Image.open("img/Item/item_3813.png").convert('RGBA')
    Forge = Forge.resize((48, 72), Image.LANCZOS)
    r, g, b, aForge = Forge.split()
    img.paste(Forge, (1330 - 50, back2.height * 2 + 25 + 276), mask=aForge)

    for h in range(4):
        for i in range(10):
            img.paste(back2, (1330 + i * back2.width, back2.height * h + 120 + 280 + 280), mask=a)
    for h in range(4):
        for i in range(10):
            draw_item(1330 + i * back2.width, back2.height * h + 120 + 280 + 280, inv[index][0], inv[index][1])  # 虚空袋
            index += 1
    Vault = Image.open("img/Item/item_4076.png").convert('RGBA')
    Vault = Vault.resize((48, 72), Image.LANCZOS)
    r, g, b, aVault = Vault.split()
    img.paste(Vault, (1330 - 50, back2.height * 2 + 25 + 280 + 276), mask=aVault)

    for h in range(10):
        img.paste(back3, (150, back2.height * h + 120 + 280 + 30), mask=a)
        img.paste(back4, (150 + back3.width, back2.height * h + 120 + 280 + 30), mask=a)
        img.paste(back5, (150 + back3.width + back4.width, back2.height * h + 120 + 280 + 30), mask=a)
    index = 59

    for h in range(10):
        draw_item(150 + back3.width + back4.width, back2.height * h + 120 + 280 + 30, inv[index][0],
                  inv[index][1])  # 盔甲饰品
        index += 1
    for h in range(10):
        draw_item(150 + back3.width, back2.height * h + 120 + 280 + 30, inv[index][0], inv[index][1])  # 盔甲饰品
        index += 1
    for h in range(10):
        draw_item(150, back2.height * h + 120 + 280 + 30, inv[index][0], inv[index][1])
        # 染料
        index += 1

    Forge = Image.open("img/Item/item_2703.png").convert('RGBA')
    Forge = Forge.resize((44, 65), Image.LANCZOS)
    r, g, b, aForge = Forge.split()
    img.paste(Forge, (155 - 50, 120 + 280 + 30), mask=aForge)
    index = 290

    for h in range(10):
        img.paste(back3, (350, back2.height * h + 120 + 280 + 30), mask=a)
        img.paste(back4, (350 + back3.width, back2.height * h + 120 + 280 + 30), mask=a)
        img.paste(back5, (350 + back3.width + back4.width, back2.height * h + 120 + 280 + 30), mask=a)
    for h in range(10):
        draw_item(350 + back3.width + back4.width, back2.height * h + 120 + 280 + 30, inv[index][0],
                  inv[index][1])  # 盔甲饰品
        index += 1
    for h in range(10):
        draw_item(350 + back3.width, back2.height * h + 120 + 280 + 30, inv[index][0], inv[index][1])  # 盔甲饰品
        index += 1
    for h in range(10):
        draw_item(350, back2.height * h + 120 + 280 + 30, inv[index][0], inv[index][1])
        # 染料
        index += 1
    Forge = Image.open("img/Item/item_2704.png").convert('RGBA')
    Forge = Forge.resize((44, 65), Image.LANCZOS)
    r, g, b, aForge = Forge.split()
    img.paste(Forge, (355 - 50, 120 + 280 + 30), mask=aForge)
    for h in range(10):
        img.paste(back3, (550, back3.height * h + 120 + 280 + 30), mask=a)
        img.paste(back4, (550 + back3.width, back2.height * h + 120 + 280 + 30), mask=a)
        img.paste(back5, (550 + back3.width + back4.width, back2.height * h + 120 + 280 + 30), mask=a)
    for h in range(10):
        draw_item(550 + back3.width + back4.width, back2.height * h + 120 + 280 + 30, inv[index][0],
                  inv[index][1])  # 盔甲饰品
        index += 1
    for h in range(10):
        draw_item(550 + back3.width, back2.height * h + 120 + 280 + 30, inv[index][0], inv[index][1])  # 盔甲饰品
        index += 1
    for h in range(10):
        draw_item(550, back3.height * h + 120 + 280 + 30, inv[index][0], inv[index][1])
        # 染料
        index += 1
    Forge = Image.open("img/Item/item_2705.png").convert('RGBA')
    Forge = Forge.resize((44, 65), Image.LANCZOS)

    r, g, b, aForge = Forge.split()
    img.paste(Forge, (555 - 50, 120 + 280 + 30), mask=aForge)
    for h in range(5):
        img.paste(back1, (750, back2.height * h + 120 + 280 + 30), mask=a)
        img.paste(back1, (750 + back2.width, back2.height * h + 120 + 280 + 30), mask=a)
    index = 89
    for h in range(5):
        draw_item(750 + back2.width, back2.height * h + 120 + 280 + 30, inv[index][0], inv[index][1])  # 坐骑宠物
        index += 1
    for h in range(5):
        draw_item(750, back2.height * h + 120 + 280 + 30, inv[index][0], inv[index][1])  # 染料
        index += 1
    Forge = Image.open("img/Item/item_2343.png").convert('RGBA')
    Forge = Forge.resize((45, 35), Image.LANCZOS)
    r, g, b, aForge = Forge.split()
    img.paste(Forge, (755 - 50, 125 + 280 + 30), mask=aForge)

    for h in range(4):
        img.paste(back1, (900, back2.height * h + 120 + 280 + 30), mask=a)
        img.paste(back1, (900 + back2.width, back2.height * h + 120 + 280 + 30), mask=a)
    index = 50
    for h in range(4):
        draw_item(900, back2.height * h + 120 + 280 + 30, inv[index][0], inv[index][1])  # 坐骑宠物
        index += 1
    for h in range(4):
        draw_item(900 + back2.width, back2.height * h + 120 + 280 + 30, inv[index][0], inv[index][1])  # 染料
        index += 1

    Forge = Image.open("img/Item/item_40.png").convert('RGBA')
    Forge = Forge.resize((25, 50), Image.LANCZOS)
    r, g, b, aForge = Forge.split()
    img.paste(Forge, (915 - 50, 120 + 280 + 30), mask=aForge)
    Trash = Image.open("img/Item/Trash.png").convert('RGBA')

    r, g, b, at = Trash.split()
    img.paste(back6, (900 + back2.width, back2.height * 4 + 120 + 280 + 30), mask=a)
    img.paste(back6, (900, back2.height * 4 + 120 + 280 + 30), mask=a)
    img.paste(Trash, (900 + 10, back2.height * 4 + 120 + 280 + 30 + 10), mask=at)
    draw_item(900 + back2.width, back2.height * 4 + 120 + 280 + 30, inv[179][0], inv[179][1])
    buffs = [i for i in buffs if i != 0]
    if len(buffs)!=0:
        index = 0
        Forge = Image.open("img/Item/item_678.png").convert('RGBA')
        Forge = Forge.resize((32, 45), Image.LANCZOS)
        r, g, b, aForge = Forge.split()
        img.paste(Forge, (712, 120 + 600 + 28), mask=aForge)
        for h in range(6):
            for b in range(8):
                if index >= len(buffs):
                    break
                draw_buff(750 + 34 * b,  + 120 + 600 + 30 + 34 * h, buffs[index])  # 染料
                index += 1


    return img
