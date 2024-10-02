import os

from PIL import Image, ImageDraw, ImageFont


def load_all_images():
    item_dir = "img/Item/"
    buff_dir = "img/Buff/"

    # 加载物品图片
    for filename in os.listdir(item_dir):
        if filename.endswith(".png") and filename.startswith("Item"):
            item_id = filename.split("_")[1].split(".")[0]
            image_cache[f"item_{item_id}"] = Image.open(os.path.join(item_dir, filename)).convert("RGBA")

    # 加载buff图片
    for filename in os.listdir(buff_dir):
        if filename.endswith(".png") and filename.startswith("Buff"):
            buff_id = filename.split("_")[1].split(".")[0]
            image_cache[f"buff_{buff_id}"] = Image.open(os.path.join(buff_dir, filename)).convert("RGBA")


# 图片缓存字典
image_cache = {}

Vault = Image.open("img/Item/item_4076.png").convert('RGBA')
Vault = Vault.resize((48, 72), Image.LANCZOS)
_, _, _, aVault = Vault.split()

Minecarts = Image.open("img/Item/item_2343.png").convert('RGBA')
Minecarts = Minecarts.resize((45, 35), Image.LANCZOS)
_, _, _, aMinecarts = Minecarts.split()

safe = Image.open("img/Item/item_346.png").convert('RGBA')
safe = safe.resize((48, 48), Image.LANCZOS)
_, _, _, asafe = safe.split()

Satchel = Image.open("img/Item/item_5343.png").convert('RGBA')
Satchel = Satchel.resize((48, 32), Image.LANCZOS)
_, _, _, aSatchel = Satchel.split()

Forge = Image.open("img/Item/item_3813.png").convert('RGBA')
Forge = Forge.resize((48, 72), Image.LANCZOS)
_, _, _, aForge = Forge.split()

WoodenArrow = Image.open("img/Item/item_40.png").convert('RGBA')
WoodenArrow = WoodenArrow.resize((25, 50), Image.LANCZOS)
_, _, _, aWoodenArrow = WoodenArrow.split()

pig = Image.open("img/Item/item_87.png").convert('RGBA')
pig = pig.resize((48, 32), Image.LANCZOS)
_, _, _, apig = pig.split()

Red_Drug = Image.open("img/Item/item_678.png").convert('RGBA')
Red_Drug = Red_Drug.resize((32, 45), Image.LANCZOS)
_, _, _, aRed_Drug = Red_Drug.split()

Trash = Image.open("img/Item/Trash.png").convert('RGBA')
_, _, _, aTrash = Trash.split()

One = Image.open("img/Item/item_2703.png").convert('RGBA')
One = One.resize((44, 65), Image.LANCZOS)
_, _, _, aOne = One.split()

Two = Image.open("img/Item/item_2704.png").convert('RGBA')
Two = Two.resize((44, 65), Image.LANCZOS)
_, _, _, aTwo = Two.split()

Three = Image.open("img/Item/item_2705.png").convert('RGBA')
Three = Three.resize((44, 65), Image.LANCZOS)
_, _, _, aThree = Three.split()

back3 = Image.open("img/Item/Inventory_Back7.png").convert('RGBA')
back4 = Image.open("img/Item/Inventory_Back8.png").convert('RGBA')
back5 = Image.open("img/Item/Inventory_Back3.png").convert('RGBA')
back1 = Image.open("img/Item/Inventory_Back.png").convert('RGBA')
back6 = Image.open("img/Item/Inventory_Back12.png").convert('RGBA')
back2 = Image.open("img/Item/Inventory_Back11.png").convert('RGBA')
_, _, _, a = back1.split()
_, _, _, a2 = back2.split()

load_all_images()

print("[查背包]图片缓存完毕...")


def get_bag_png(name: str, inv, buffs):
    font = "font/LXGWWenKaiMono-Medium.ttf"
    img = Image.open("img/lookbag_bg.png").convert('RGBA')

    ft = ImageFont.truetype(font=font, size=100)

    w, h = img.size
    text_w, text_h = ft.getsize(name)
    draw = ImageDraw.Draw(img)
    draw.text(((w - text_w) / 2, 0), name, font=ft)
    draw = ImageDraw.Draw(img)
    size = 25

    def draw_item(x: int, y: int, id: int, stack: int):
        try:
            # 从缓存中获取图片
            item = image_cache.get(f"item_{id}")
            if item is None:
                raise ValueError(f"Image with ID {id} not found in cache.")

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

            ft = ImageFont.truetype(font="font/LXGWWenKaiMono-Medium.ttf", size=14)

            r, g, b, a = item.split()
            img.paste(item, (x + 13, y + 13), mask=a)
            if stack != 1 and stack != 0:
                draw.text((x + 6, y + 30), str(stack), font=ft)
        except Exception as e:
            print(f"Error: {e}")
            pass

    def draw_buff(x: int, y: int, id: int):
        try:
            if id == 0:
                return
            # 从缓存中获取图片
            buff = image_cache.get(f"buff_{id}")
            if buff is None:
                raise ValueError(f"Buff image with ID {id} not found in cache.")

            _, _, _, a2 = buff.split()
            img.paste(buff, (x, y), mask=a2)
        except Exception as e:
            print(f"Error: {e}")
            pass

    for h in range(5):
        for i in range(10):
            img.paste(back1, (150 + i * back1.width, back1.height * h + 120), mask=a)  # 背包
    index = 0
    for h in range(5):
        for i in range(10):
            draw_item(150 + i * back1.width, back1.height * h + 120, inv[index][0], inv[index][1])
            index += 1

    img.paste(Satchel, (150 - 50, Satchel.height * 3 + 35), mask=aSatchel)

    for h in range(4):
        for i in range(10):
            img.paste(back2, (740 + i * back2.width, back2.height * h + 120), mask=a2)  # 猪猪
    index = 99

    for h in range(4):
        for i in range(10):
            draw_item(740 + i * back2.width, back2.height * h + 120, inv[index][0], inv[index][1])
            index += 1

    img.paste(pig, (740 - 50, back2.height * 2 + 25), mask=apig)
    for h in range(4):
        for i in range(10):
            img.paste(back2, (1330 + i * back2.width, back2.height * h + 120), mask=a)  # 保险
    for h in range(4):
        for i in range(10):
            draw_item(1330 + i * back2.width, back2.height * h + 120, inv[index][0], inv[index][1])
            index += 1

    img.paste(safe, (1330 - 50, back2.height * 2 + 21), mask=asafe)

    index += 1

    for h in range(4):
        for i in range(10):
            img.paste(back2, (1330 + i * back2.width, back2.height * h + 120 + 280), mask=a)  # 熔炉
    for h in range(4):
        for i in range(10):
            draw_item(1330 + i * back2.width, back2.height * h + 120 + 280, inv[index][0], inv[index][1])
            index += 1

    img.paste(Forge, (1330 - 50, back2.height * 2 + 25 + 276), mask=aForge)

    for h in range(4):
        for i in range(10):
            img.paste(back2, (1330 + i * back2.width, back2.height * h + 120 + 280 + 280), mask=a)
    for h in range(4):
        for i in range(10):
            draw_item(1330 + i * back2.width, back2.height * h + 120 + 280 + 280, inv[index][0], inv[index][1])  # 虚空袋
            index += 1

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

    img.paste(One, (155 - 50, 120 + 280 + 30), mask=aOne)
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

    img.paste(Two, (355 - 50, 120 + 280 + 30), mask=aTwo)
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

    img.paste(Three, (555 - 50, 120 + 280 + 30), mask=aThree)
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

    img.paste(Minecarts, (755 - 50, 125 + 280 + 30), mask=aMinecarts)

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

    img.paste(WoodenArrow, (915 - 50, 120 + 280 + 30), mask=aWoodenArrow)

    img.paste(back6, (900 + back2.width, back2.height * 4 + 120 + 280 + 30), mask=a)
    img.paste(back6, (900, back2.height * 4 + 120 + 280 + 30), mask=a)
    img.paste(Trash, (900 + 10, back2.height * 4 + 120 + 280 + 30 + 10), mask=aTrash)
    draw_item(900 + back2.width, back2.height * 4 + 120 + 280 + 30, inv[179][0], inv[179][1])
    buffs = [i for i in buffs if i != 0]
    if len(buffs) != 0:
        index = 0

        img.paste(Red_Drug, (712, 120 + 600 + 28), mask=aRed_Drug)
        for h in range(6):
            for b in range(8):
                if index >= len(buffs):
                    break
                draw_buff(750 + 34 * b, + 120 + 600 + 30 + 34 * h, buffs[index])
                index += 1

    return img
