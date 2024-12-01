from io import BytesIO
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from PIL import Image


class EdgeHelper:
    @staticmethod
    def trim_and_add_whitespace(img, threshold=20, white_space_rows=5):
        bottom_pixel = img.getpixel((0, img.size[1] - 1))
        for y in range(img.size[1] - 1, -1, -1):
            row = [img.getpixel((x, y)) for x in range(img.size[0])]
            if sum(1 for pixel in row if pixel != bottom_pixel) > threshold:
                img = img.crop((0, 0, img.size[0], y + 1))
                break

        new_height = img.height + white_space_rows
        new_img = Image.new(img.mode, (img.width, new_height), (255, 255, 255))  # 创建白色背景的新图像
        new_img.paste(img, (0, 0))

        return new_img

    @staticmethod
    def get_web_png(url: str):
        edge_driver_path = 'msedgedriver.exe'
        service = Service(edge_driver_path)
        options = webdriver.EdgeOptions()
        options.add_argument('headless')  # 无头模式

        driver = webdriver.Edge(service=service, options=options)
        driver.get(url)  # 访问目标网页

        classes_to_remove = ['HeaderMktg', 'header-logged-out', 'footer', 'discussion-timeline-actions']

        for class_name in classes_to_remove:
            elements_to_remove = driver.find_elements(By.CSS_SELECTOR, f'.{class_name}')
            for element in elements_to_remove:
                driver.execute_script("arguments[0].remove();", element)

        width = driver.execute_script("return document.documentElement.scrollWidth")
        height = driver.execute_script("return document.documentElement.scrollHeight")
        driver.set_window_size(width, height)
        im = Image.open(BytesIO(driver.get_screenshot_as_png()))
        driver.quit()

        im = EdgeHelper.trim_and_add_whitespace(im)
        return im


# EdgeHelper.get_web_png("https://github.com/UnrealMultiple/TShockPlugin/pull/565#issuecomment-2480622951").show()