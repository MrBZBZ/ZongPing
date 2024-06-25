import threading
import time
from tkinter import messagebox
import wx
import requests as re
import tkinter as tk
import base64 as bs
from io import BytesIO
from PIL import Image, ImageTk
#请注意自行更改接口，不同省份的接口不同，请自行更改
#不同省份获取到的数据可能也有差异，我写的解析器可能无法解析，请自行修改
def get_header():#这是一个公共函数，用于获取header
    with open('config.txt', 'r') as file:
        content = file.read()
    header = {
        "Authorization": "Bearer " + content,#这个content的值就是获取到的Token
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
        "Referer": "https://zhszpjxsd.gxeduyun.edu.cn/",
    }
    return header
class MyFrame(wx.Frame):
    def __init__(self, parent, title):
        ways1 = ['不筛选', '筛选指定姓名']
        ways2 = ['全校范围', '全班范围']
        super(MyFrame, self).__init__(parent, title=title, size=(480, 480))
        self.panel = wx.Panel(self)

        # 新增输出面板
        self.output_panel = wx.ScrolledWindow(self.panel, -1, style=wx.SUNKEN_BORDER)
        self.output_text = wx.TextCtrl(self.output_panel, style=wx.TE_READONLY | wx.TE_MULTILINE | wx.HSCROLL)
        # 设置输出面板的滚动条
        self.output_panel.SetVirtualSize((0, 0))  # 初始化虚拟大小为0
        self.output_panel.SetScrollRate(10, 10)  # 设置滚动速率

        self.begin_label = wx.StaticText(self.panel, label="从第？页开始：")
        self.begin_input = wx.TextCtrl(self.panel)
        self.end_label = wx.StaticText(self.panel, label="到第？页结束：")
        self.end_input = wx.TextCtrl(self.panel)
        self.wayChoice1 = wx.Choice(self.panel, choices=ways1)
        self.name = wx.StaticText(self.panel, label="姓名：")
        self.name_input = wx.TextCtrl(self.panel)
        self.wayChoice2 = wx.Choice(self.panel, choices=ways2)
        self.wayChoice1.SetSelection(0)
        self.wayChoice2.SetSelection(0)
        self.start_button = wx.Button(self.panel, label="开始爬取数据")
        self.output = wx.StaticText(self.panel, label="输出：")

        sizer = wx.BoxSizer(wx.VERTICAL)
        sizer.Add(self.begin_label, 0, wx.ALL, 5)
        sizer.Add(self.begin_input, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(self.end_label, 0, wx.ALL, 5)
        sizer.Add(self.end_input, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(self.wayChoice1, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(self.name, 0, wx.ALL, 5)
        sizer.Add(self.name_input, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(self.wayChoice2, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(self.start_button, 0, wx.ALL | wx.EXPAND, 5)
        sizer.Add(self.output, 0, wx.ALL, 5)

        output_sizer = wx.BoxSizer(wx.VERTICAL)
        output_sizer.Add(self.output_text, 1, wx.EXPAND)
        self.output_panel.SetSizer(output_sizer)
        self.output_panel.SetInitialSize((50, 50))
        sizer.Add(self.output_panel, 1, wx.EXPAND | wx.LEFT | wx.RIGHT | wx.BOTTOM, 5)

        self.Bind(wx.EVT_CLOSE, self.on_close)
        self.start_button.Bind(wx.EVT_BUTTON, self.new_start)

        self.begin_input.SetValue("1")
        self.end_input.SetValue("100")
        self.panel.SetSizer(sizer)
        self.last_size = None
        self.Center()

    def on_close(self, event):
        self.Destroy()
        app.ExitMainLoop()
    def new_start(self, event):
        threading.Thread(target=self.start).start()
    def start(self):
        begin = int(self.begin_input.GetValue())
        end = int(self.end_input.GetValue())
        header = get_header()
        if self.wayChoice2.GetSelection() == 0:
            url = "https://zhszpjapi.gxeduyun.edu.cn/record/school/circle/getListPage"#全校范围的接口，对此接口发送请求将获得全校数据
        else:
            url = "https://zhszpjapi.gxeduyun.edu.cn/record/circle/getListPage"#全班范围的接口，对此接口发送请求将获得全班数据(你用的账号是哪个班的就是获得哪个班数据)
        with open("response.txt", "a", encoding="utf-8") as file:  # 使用追加模式打开文件
            for pageIndex in range(begin, end+1):  # 循环
                params = {
                    'application': "student",
                    'system-env': "guangxi-gz",
                    'pageIndex': str(pageIndex),  # 将pageIndex转换为字符串
                    'pageSize': "10"
                }
                response = re.get(url, params=params, headers=header).json()
                if self.wayChoice1.GetSelection() == 1:#如果为筛选(启动名字筛选的逻辑，筛选指定姓名的人发送的综评记录)
                    for record in response["data"]["list"]:
                        if record["submitterName"] == self.name_input.GetValue():
                            filtered_info = (
                                f"ID: {record['submitterName']}, \n"
                                f"标题: {record['title']}, \n"
                                f"内容: {record['content']}, \n"
                                f"类别: {record['categoryName']}\n\n"
                            )
                            file.write(filtered_info)  # 写入筛选后的信息到文件
                            print(f"已保存记录 - ID: {record['submitterName']}")
                    print(f"已保存第{pageIndex}页响应")
                    self.output_text.AppendText(f"已保存第{pageIndex}页响应\n")
                    # self.output_text.SetSizeHints(self.output_text.GetSize()[0], -1)  # 更新宽度
                    # self.output_text.SetVirtualSize((-1, self.output_text.GetLastPosition() + 10))  # 更新虚拟高度
                    # self.output_panel.FitInside()  # 调整内部大小以适应内容
                    # self.output_panel.Refresh()  # 刷新输出面板
                    wx.Yield()  # 确保界面更新
                    time.sleep(2)
                else:#如果为不筛选
                    for record in response["data"]["list"]:
                        filtered_info = (
                            f"ID: {record['submitterName']}, \n"
                            f"标题: {record['title']}, \n"
                            f"内容: {record['content']}, \n"
                            f"类别: {record['categoryName']}\n\n"
                        )
                        file.write(filtered_info)  # 写入筛选后的信息到文件
                        print(f"已保存记录 - ID: {record['submitterName']}")
                    print(f"已保存第{pageIndex}页响应")
                    self.output_text.AppendText(f"已保存第{pageIndex}页响应\n")
                    # self.output_text.SetSizeHints(self.output_text.GetSize()[0], -1)  # 更新宽度
                    # self.output_text.SetVirtualSize((-1, self.output_text.GetLastPosition() + 10))  # 更新虚拟高度
                    # self.output_panel.FitInside()  # 调整内部大小以适应内容
                    # self.output_panel.Refresh()  # 刷新输出面板
                    wx.Yield()  # 确保界面更新
                    time.sleep(2)

if __name__ == "__main__":
    #登录界面设置
    def start():
        header = get_header()
        result = re.post("https://zhszpjapi.gxeduyun.edu.cn/record/recommend/checkIsOpenRecommend",headers=header).json()#这个是在检查之前保存的Cookie还有没有用，没有用就启动登录界面
        if(result["success"]):
            root.destroy()
            frame = MyFrame(None, "综评系统爬虫1.0 by 酥叶Leaves_awa")
            frame.Show()
            app.MainLoop()#启动爬虫界面
        else:
            root.mainloop()#启动登录界面
    def login():
        data = {
            "usernameOrEmail": entry_username.get(),#用户名
            "password": entry_password.get(),#密码
            "validateCode": entry_ValidateCode.get(),#验证码
            "flag": flag,#验证码flag
            "loginWebType": "0",#登录类型
            "application": "teacher",#这两个不用管，你抓到接口里面用的什么就改成什么参数，没有就删掉
            "system-env": "guangxi-gz"#这两个不用管，你抓到接口里面用的什么就改成什么参数，没有就删掉
        }
        login = re.post("https://zhszpjapi.gxeduyun.edu.cn/auth/guangxiAuth", data=data).json()#发送登录请求到系统
        if login["success"]:
            with open("config.txt", "w") as f:
                f.write(str(login["data"]["token"]))
            messagebox.showinfo("登录状态", "登录成功，token已保存到config.txt")
            start()
        else:
            messagebox.showinfo("登录状态", "登录失败，请重试")
    app = wx.App(False)
    ValidateCode = re.get("https://zhszpjapi.gxeduyun.edu.cn/auth/validateCode?system-env=guangxi-gz").json()#这个是获取验证码图片的接口
    flag = ValidateCode['data']['flag']
    imgsrc = ValidateCode['data']['imgsrc']
    img_data = bs.b64decode(imgsrc)
    img = Image.open(BytesIO(img_data))
    # 保存图片到本地
    img.save('captcha.png')#我只做了可以让程序获取一次验证码的逻辑，如果验证码输错了只能关掉窗口重新打开

    def on_close():
        messagebox.showwarning("警告", "你并未完成登录！")
        root.destroy()
    def center_window(root, width, height):
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        root.geometry(f"{width}x{height}+{x}+{y}")
    # 创建主窗口
    root = tk.Tk()
    root.title("登录到综合素质评价系统")
    root.protocol("WM_DELETE_WINDOW", on_close)  # 绑定窗口关闭事件
    win_width = 350
    win_height = 250
    # 设置窗口大小
    center_window(root, win_width, win_height)

    # 用户名标签和输入框
    label_username = tk.Label(root, text="用户名:")
    label_username.pack()
    entry_username = tk.Entry(root)
    entry_username.pack()

    # 密码标签和输入框
    label_password = tk.Label(root, text="密码:")
    label_password.pack()
    entry_password = tk.Entry(root, show="*")  # 使用show参数使密码显示为星号
    entry_password.pack()

    ValidateCode = tk.Label(root, text="验证码:")
    ValidateCode.pack()
    entry_ValidateCode = tk.Entry(root)
    entry_ValidateCode.pack()

    # 加载并转换为Tkinter PhotoImage对象
    captcha_image = Image.open('captcha.png')
    captcha_photo_image = ImageTk.PhotoImage(captcha_image)

    # 创建Label来显示图片
    label_captcha_image = tk.Label(root, image=captcha_photo_image)
    label_captcha_image.pack()  # 放置在适当位置

    # 保持对PhotoImage对象的引用
    label_captcha_image.image = captcha_photo_image

    # 登录按钮
    button_login = tk.Button(root, text="登录", command=login)
    button_login.pack()
    if(True):
        try:
            with open('config.txt', 'r') as file:
                content = file.read()
            # 检查文件内容是否为空
            if content == "":
                root.mainloop()
            else:
                start()
        except FileNotFoundError:
            root.mainloop()