import time

from PIL import Image, ImageDraw, ImageFont


def get_process_png(data) -> Image:
    progress = data["result"]
    img = Image.open("img/progress_bg.png")
    ft = ImageFont.truetype(font="font/LXGWWenKaiMono-Medium.ttf", size=100)
    draw = ImageDraw.Draw(img)
    w, h = img.size
    text_w, text_h = ft.getsize(data["worldname"])
    draw.text(((w - text_w) / 2, 0), data["worldname"], font=ft)

    ft = ImageFont.truetype(font="font/LXGWWenKaiMono-Medium.ttf", size=60)
    draw = ImageDraw.Draw(img)
    text_w, text_h = ft.getsize("进度")
    draw.text(((w - text_w) / 2, 150), "进度", font=ft)

    ft = ImageFont.truetype(font="font/LXGWWenKaiMono-Medium.ttf", size=30)
    draw = ImageDraw.Draw(img)
    draw.text((10, 1040), "Copy from Qianyi", font=ft)
    draw.text((310, 1040), time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), font=ft)
    row = 0
    column = 0
    add = 0

    for m in progress:
        for i in m.values():
            if row == 2 and column == 0:
                if i:
                    ft = ImageFont.truetype(font="font/LXGWWenKaiMono-Medium.ttf", size=30)
                    draw = ImageDraw.Draw(img)
                    draw.text((270 + row * 230 + 20, 440 + column * 250), "已击败", font=ft, fill="red")

                    ft = ImageFont.truetype(font="font/LXGWWenKaiMono-Medium.ttf", size=30)
                    draw = ImageDraw.Draw(img)
                    draw.text((270 + (row + 1) * 230 + 100, 440 + column * 250), "已击败", font=ft, fill="red")
                else:
                    ft = ImageFont.truetype(font="font/LXGWWenKaiMono-Medium.ttf", size=30)
                    draw = ImageDraw.Draw(img)
                    draw.text((270 + row * 230 + 20, 440 + column * 250), " 未击败", font=ft, fill="black")

                    ft = ImageFont.truetype(font="font/LXGWWenKaiMono-Medium.ttf", size=30)
                    draw = ImageDraw.Draw(img)
                    draw.text((270 + (row + 1) * 230 + 100, 440 + column * 250), " 未击败", font=ft, fill="black")
                row += 2
                continue
            if row == 2:
                add = 20
            if row >= 3:
                add = 100 + (row - 3) * 40
                if row == 5:
                    add -= 40
            if i:
                ft = ImageFont.truetype(font="font/LXGWWenKaiMono-Medium.ttf", size=30)
                draw = ImageDraw.Draw(img)
                draw.text((270 + row * 230 + add, 440 + column * 250), "已击败", font=ft, fill="red")
            else:
                ft = ImageFont.truetype(font="font/LXGWWenKaiMono-Medium.ttf", size=30)
                draw = ImageDraw.Draw(img)
                draw.text((270 + row * 230 + add, 440 + column * 250), " 未击败", font=ft, fill="black")
            if row == 5:
                row = 0
                column += 1
                add = 0
            else:
                row += 1

    return img
