import time

from PIL import Image, ImageDraw, ImageFont

ft_25 = ImageFont.truetype(font="font/LXGWWenKaiMono-Medium.ttf", size=25)
ft_30 = ImageFont.truetype(font="font/LXGWWenKaiMono-Medium.ttf", size=30)
ft_40 = ImageFont.truetype(font="font/LXGWWenKaiMono-Medium.ttf", size=40)
ft_60 = ImageFont.truetype(font="font/LXGWWenKaiMono-Medium.ttf", size=60)
ft_100 = ImageFont.truetype(font="font/LXGWWenKaiMono-Medium.ttf", size=100)

def transparent_back(img):
    img = img.convert('RGBA')
    L, H = img.size

    for i in range(10):
        for h in range(H):
            color_0 = img.getpixel((i, h))
            for l in range(L):
                dot = (l, h)
                color_1 = img.getpixel(dot)
                if color_1 == color_0:
                    color_1 = color_1[:-1] + (0,)
                    img.putpixel(dot, color_1)
    return img


def get_process_png(process_data) -> Image:
    process = process_data["process"]
    kill_counts = process_data["kill_counts"]
    if process_data["zenith_world"]:
        img = Image.open("img/Background_2.png")
    elif process_data["drunk_world"]:
        img = Image.open("img/Background_3.png")
    else:
        img = Image.open("img/Background_1.png")

    draw = ImageDraw.Draw(img)

    def draw_event(name,show_name,x,y):
        event_img = Image.open(f"img/process/{name}.png")
        if event_img.mode != 'RGBA':
            event_img = event_img.convert('RGBA')
            event_img.save(f"img/process/{name}.png")
        _, _, _, ba = event_img.split()
        img.paste(event_img, (x, y), mask=ba)
        _, _, tw, th = draw.textbbox((0, 0), show_name + ":", font=ft_25)
        draw.text((x + event_img.size[0], y), show_name+ ":", font=ft_25)
        print(x + event_img.size[0])
        if name == "Old Ones Army":
            if process['DD2InvasionT3']:
                draw.text((x + event_img.size[0] + tw, y), "T1", font=ft_25,
                          fill='blue')
            elif process['DD2InvasionT2']:
                draw.text((x + event_img.size[0] + tw, y), "T2", font=ft_25,
                          fill='orange')
            elif process['DD2InvasionT1']:
                draw.text((x + event_img.size[0] + tw, y), "T3", font=ft_25,
                          fill='red')
            else:
                draw.text((x + event_img.size[0] + tw, y), "未击败", font=ft_25,
                          fill='gray')
            return
        if name == "Pillars":
            if process[name]:
                draw.text((x + event_img.size[0] + tw, y), "已击败", font=ft_25, fill='red')
            else:
                notDefeat = []
                if not process['Tower Stardust']:
                    notDefeat.append("星尘")
                if not process['Tower Vortex']:
                    notDefeat.append("星璇")
                if not process['Tower Nebula']:
                    notDefeat.append("星云")
                if not process['Tower Solar']:
                    notDefeat.append("日耀")
                draw.text((x + event_img.size[0] + tw, y), f"未击败({','.join(notDefeat)})", font=ft_25,
                          fill='gray')
        if process[name]:
            draw.text((x + event_img.size[0] + tw, y), "已击败", font=ft_25, fill='red')
        else:
            draw.text((x + event_img.size[0] + tw, y), "未击败", font=ft_25,
                      fill='gray')

    def draw_boss(name, x, y, up=0):
        boss_img = Image.open(f"img/process/{name}.png")
        if boss_img.mode != 'RGBA':
            boss_img = boss_img.convert('RGBA')
            boss_img.save(f"img/process/{name}.png")
        _, _, _, ba = boss_img.split()
        img.paste(boss_img, (x, y - up), mask=ba)
        _, _, tw, th = draw.textbbox((0, 0), "已击败", font=ft_40)

        print(x + boss_img.size[0] / 2 - tw / 2, y + boss_img.size[1] - 695 - 207)
        if name == "Mechdusa":
            if process['The Destroyer'] and process['The Twins'] and process['Skeletron Prime']:
                _, _, tw, th = draw.textbbox((0, 0), "已击败", font=ft_40)
                draw.text((x + boss_img.size[0] / 2 - tw / 2, y + boss_img.size[1] + 10), "已击败", font=ft_40,
                          fill='red')
            else:
                notDefeat = []
                if not process['The Destroyer']:
                    notDefeat.append("毁")
                if not process['Skeletron Prime']:
                    notDefeat.append("骷")
                if not process['The Twins']:
                    notDefeat.append("眼")

                _, _, tw, th = draw.textbbox((0, 0), f"未击败({','.join(notDefeat)})", font=ft_40)
                draw.text((x + boss_img.size[0] / 2 - tw / 2, y + boss_img.size[1] + 10), f"未击败({','.join(notDefeat)})", font=ft_40)

            return
        if process[name]:
            _, _, tw, th = draw.textbbox((0, 0), f"已击败({kill_counts[name]}次)", font=ft_40)
            draw.text((x + boss_img.size[0] / 2 - tw / 2, y + boss_img.size[1] + 10), f"已击败({kill_counts[name]}次)", font=ft_40, fill='red')
        else:
            _, _, tw, th = draw.textbbox((0, 0), "未击败", font=ft_40)
            if process_data['zenith_world']:
                draw.text((x + boss_img.size[0] / 2 - tw / 2, y + boss_img.size[1] + 10), "未击败", font=ft_40)
            else:
                draw.text((x + boss_img.size[0] / 2 - tw / 2, y + boss_img.size[1] + 10), "未击败", font=ft_40,
                          fill='black')

    MAX_W, MAX_H = img.size

    if len(process_data["worldname"])>7:
        process_data["worldname"] = process_data["worldname"][:6]+"..."

    _, _, w, h = draw.textbbox((0, 0), process_data["worldname"], font=ft_100)
    draw.text(((MAX_W - w) / 2, 0), process_data["worldname"], font=ft_100)

    icon = transparent_back(Image.open(f"img/world_icon/{process_data['world_icon']}.png"))
    icon = icon.resize((int(160 * 0.65), int(158 * 0.65)))
    _, _, _, a = icon.split()
    img.paste(icon, (int((MAX_W - w) / 2 - 160 * 0.65), 0), mask=a)

    _, _, w, h = draw.textbbox((0, 0), "进度", font=ft_60)
    draw.text(((MAX_W - w) / 2, 120), "进度", font=ft_60)



    draw.text((10, 1040), "By Cai", font=ft_30)  # 署名
    draw.text((150, 1040), time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), font=ft_30)  # 时间

    draw_event("Goblins","哥布林军队",200,50)
    draw_event("Pirates", "海盗入侵", 200+2, 50 + 24 *1 )
    draw_event("Frost", "雪人军团", 200+6, 50 + 24 * 2)
    draw_event("Frost Moon", "霜月", 200+4, 50 + 24 * 3)
    draw_event("Pumpkin Moon", "南瓜月", 200+4, 50 + 24 * 4)
    draw_event("Pillars", "四柱", 200+2, 50 + 24 * 5)
    draw_event("Old Ones Army", "旧日军团", 200, 50 + 24 * 6)

    draw_boss("King Slime", 180 + 280 * 0, 250)
    draw_boss("Eye of Cthulhu", 180 + 280 * 1 + 20, 250 - 10)
    draw_boss("Eater of Worlds", 180 + 280 * 2, 250 + 133, 50)
    draw_boss("Brain of Cthulhu", 180 + 280 * 3, 250 - 3)
    draw_boss("Queen Bee", 180 + 280 * 4, 250 + 18)
    draw_boss("Deerclops", 180 + 280 * 5, 250 - 47)
    draw_boss("Skeletron", 180 + 280 * 0 - 2, 250 * 2)
    draw_boss("Wall of Flesh", 180 + 280 * 1 + 25, 250 * 2 - 5)
    draw_boss("Queen Slime", 180 + 280 * 2 + 4, 250 * 2 + 53)
    if process_data['zenith_world']:
        draw_boss("Duke Fishron", 180 + 280 * 3, 250 * 2 + 70)
        draw_boss("Mechdusa", 180 + 280 * 4 + 80, 250 * 2 + 30)
        draw_boss("Plantera", 180 + 280 * 0 + 25, 250 * 3 + 30)
        draw_boss("Golem", 180 + 280 * 1 + 9, 250 * 3 + 30 - 47, -20)
        draw_boss("Empress of Light", 180 + 280 * 2 - 31, 250 * 3 + 30 + 21)
        draw_boss("Lunatic Cultist", 180 + 280 * 3 + 64, 250 * 3 + 30 + 92, 30)
        draw_boss("Moon Lord", 180 + 280 * 4 -1, 250 * 3 + 30 + 4)
    else:
        draw_boss("The Destroyer", 180 + 280 * 3, 250 * 2 + 174, 50)
        draw_boss("The Twins", 180 + 280 * 4 + 23, 250 * 2 - 5)
        draw_boss("Skeletron Prime", 180 + 280 * 5 + 4, 250 * 2 - 4)
        draw_boss("Plantera", 180 + 280 * 0 + 25, 250 * 3 + 30)
        draw_boss("Golem", 180 + 280 * 1 + 9, 250 * 3 + 30 - 47, -20)
        draw_boss("Duke Fishron", 180 + 280 * 2, 250 * 3 + 30 + 27)
        draw_boss("Empress of Light", 180 + 280 * 3 - 31, 250 * 3 + 30 + 21)
        draw_boss("Lunatic Cultist", 180 + 280 * 4 + 63, 250 * 3 + 30 + 92,30)
        draw_boss("Moon Lord", 180 + 280 * 5 - 20, 250 * 3 + 30 + 4)

    return img


if __name__ == '__main__':
    data = {"status": "200", "type": "process",
            "process":
                {
                    "King Slime": False,
                    "Pumpkin Moon": False,
                    "Frost Moon" : True,
                    "Eye of Cthulhu": True,
                    "Eater of Worlds or Brain of Cthulhu": False,
                    "Eater of Worlds": False,
                    "Brain of Cthulhu": True,
                    "Queen Bee": True,
                    "Deerclops": True,
                    "Skeletron": True,
                    "Wall of Flesh": False,
                    "Queen Slime": True,
                    "The Destroyer": True,
                    "The Twins": True,
                    "Skeletron Prime": False,
                    "Plantera": False,
                    "Golem": False,
                    "Duke Fishron": False,
                    "Empress of Light": False,
                    "Lunatic Cultist": False,
                    "Moon Lord": False,
                    "Pillars": False,
                    "Tower Stardust": True,
                    "Tower Vortex": False,
                    "Tower Nebula": True,
                    "Tower Solar": False,
                    "Goblins": True,
                    "Pirates": False,
                    "Frost": True,
                    "Martians": False,
                    "DD2InvasionT1": True,
                    "DD2InvasionT2": True,
                    "DD2InvasionT3": False
                },
            "kill_counts": {
                "King Slime": 1,
                "Eye of Cthulhu": 3,
                "Eater of Worlds": 5,
                "Brain of Cthulhu": 66,
                "Queen Bee": 3,
                "Deerclops": 4,
                "Skeletron": 32,
                "Wall of Flesh": 34,
                "Queen Slime": 4,
                "The Destroyer": 3,
                "The Twins": 4,
                "Skeletron Prime": 5,
                "Plantera": 7,
                "Golem": 5,
                "Duke Fishron": 4,
                "Empress of Light": 4,
                "Lunatic Cultist": 5,
                "Moon Lord": 9
            },
            "worldname": "啊da啊啊啊啊aaaaaa...",
            "drunk_world": False,
            "zenith_world": False,
            "world_icon": "IconHallowCrimsonNotTheBees",
            "group": 991556763
            }
    get_process_png(data).show()
