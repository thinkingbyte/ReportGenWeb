import tkinter
from PIL import ImageGrab
from selenium import webdriver
import time


# 工具类，用于屏幕截屏
class ScreenCut():
    def __init__(self, url, name):
        self.url = url
        self.name = name

    def cutScreen(self):
        try:
            chrome_driver = 'C:\Program Files (x86)\Google\Chrome\Application\chromedriver.exe'  # chromedriver的文件位置
            b = webdriver.Chrome(executable_path=chrome_driver)
            # 设置浏览器大小
            b.maximize_window()
            b.get(self.url)

            # print (b.get_window_size())
            # b.set_window_size(1280,800) # 分辨率 1280*800

            # tkinter初始化，获取当前屏幕分辨率
            win = tkinter.Tk()
            width = win.winfo_screenwidth()
            height = win.winfo_screenheight()
            time.sleep(1);
            img = ImageGrab.grab(bbox=(0, 0, width, height - 50))
            img.save("./static/image/" + self.name + '.jpg')
            # 关闭浏览器
            b.quit()
        except:
            print("截屏失败")
            exit(-1)


