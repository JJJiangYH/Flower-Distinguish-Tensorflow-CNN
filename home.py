from tkinter import Button, Entry, Label, Frame, Tk, StringVar
from tkinter import messagebox
from tkinter.filedialog import askopenfilenames

import numpy as np

from flowerTrain.train import Train
from login import *
from trainTest import evaluate_one_image

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

path = os.path.dirname(__file__)  # 工程真实路径
picSize = 150  # 图片需要调整为的尺寸
topWidth = 450  # 窗口宽度
topheight = 700  # 窗口长度
picNum = 9  # 能显示的图片个数
imageList = list()  # [picSize x picSize的原图片,picSize x picSizeTk转换图片]组成的二维列表
picLabel = list()  # 显示图片的标签所组成的列表

del_index_entey = None
image_x = None  # X图片

batch_size_entry = None
max_step_entry = None
learning_rate_entry = None
train_btn = None
test_index_entry = None
home = None


# 窗口实例化函数
def create_win(title, size):
	top = Tk()  # 实例化一个窗口
	top.title(title)  # 设置窗口名
	# 窗口居中
	screenwidth = top.winfo_screenwidth()
	screenheight = top.winfo_screenheight()
	alignstr = '%dx%d+%d+%d' % (topWidth, topheight, (screenwidth - topWidth) / 2, (screenheight - topheight) / 2)
	top.geometry(alignstr)

	return top


# 向框架中添加九个白色的用于显示图片的label
def create_label():
	# 实例化一个装图片的框架
	global picLabel
	global image_x
	global home, picSize, path

	# 给标签初始化一张图片
	image = Image.open(path + '/X.jpg').resize((picSize, picSize))
	image_x = ImageTk.PhotoImage(image)

	picFrame = Frame(home, width=picSize * 3, height=picSize * 3, bg='white')
	picFrame.grid(row=0)

	for i in range(9):
		picLabel.append(Label(picFrame, width=picSize, height=picSize, image=image_x, bg='white'))
		picLabel[i].place(x=picSize * (i % 3), y=picSize * (i // 3))


# 实例化一个操作图片的框架,并向其中添加操控控件
def create_control():
	global del_index_entey
	global home

	Label(home).grid(row=1)

	# 添加文件的按钮
	add_btn = Button(home, text='添加图片', command=addpic)
	add_btn.grid(row=2)

	# 实例化一个操作图片的框架
	btn_frame = Frame(home, width=picSize * 3, height=150)
	btn_frame.grid(row=3)

	# 删除提示
	Label(btn_frame, text='请输入要删除的图片标号（1-9）').grid(row=3, column=0)

	# 设置默认索引号
	index_default_value = StringVar()
	index_default_value.set('1')

	# 删除图片的序号输入框
	del_index_entey = Entry(btn_frame, textvariable=index_default_value)
	del_index_entey.grid(row=3, column=1)

	# 图片删除按钮
	remove_btn = Button(btn_frame, text='删除图片', command=delpic)
	remove_btn.grid(row=3, column=2)

	Label(home).grid(row=4)


# 实例化一个调节训练参数的框架
def create_train():
	global batch_size_entry, max_step_entry, learning_rate_entry, train_btn, test_index_entry
	global home

	# 声明变量
	batch_default = StringVar()
	step_default = StringVar()
	rate_default = StringVar()
	test_default = StringVar()

	# 实例化框架
	train_frame = Frame(home, width=450, height=100)
	train_frame.grid(row=5)

	# 批次 默认20
	batch_default.set('20')
	Label(train_frame, text='批次').grid(row=0, column=0)
	batch_size_entry = Entry(train_frame, textvariable=batch_default)
	batch_size_entry.grid(row=0, column=1)

	# 轮次 默认1000
	step_default.set('1000')
	Label(train_frame, text='轮次').grid(row=1, column=0)
	max_step_entry = Entry(train_frame, textvariable=step_default)
	max_step_entry.grid(row=1, column=1)

	# 学习率 默认0.0001
	rate_default.set('0.0001')
	Label(train_frame, text='学习率').grid(row=2, column=0)
	learning_rate_entry = Entry(train_frame, textvariable=rate_default)
	learning_rate_entry.grid(row=2, column=1)

	# 训练按钮
	train_btn = Button(train_frame, text='开始训练', command=train)
	train_btn.grid(row=0, column=3, rowspan=3)

	# 识别图片序号输入
	test_default.set('1')
	Label(train_frame, text='要识别的序号').grid(row=3, column=0)
	test_index_entry = Entry(train_frame, textvariable=test_default)
	test_index_entry.grid(row=3, column=1)

	# 识别按钮
	test_btn = Button(train_frame, text='开始识别', command=test)
	test_btn.grid(row=3, column=2, columnspan=2)


# addbotton响应函数
def addpic():
	picchoose()  # 选择图片
	label_picdisplay()  # 在标签上输出


# 图片选择处理函数
def picchoose():
	paths = askopenfilenames(title='选择图片', filetypes=[('JPG', '*.jpg')])
	openpic(paths)


# 图片打开、处理函数
def openpic(picName):
	global imageList

	for i in picName[0:9]:
		t = Image.open(i).resize((picSize, picSize))
		imageList.append([t, ImageTk.PhotoImage(t)])


# 将选择的图片在标签中显示
def label_picdisplay():
	global picLabel
	global imageList

	for i in range(9):
		if i >= len(imageList):
			picLabel[i].config(image=image_x)
		else:
			picLabel[i].config(image=imageList[i][1])


# 图片删除函数
def delpic():
	global imageList
	global del_index_entey

	del_index = eval(del_index_entey.get())  # 获取要删除的图片序号
	try:
		imageList.pop(del_index - 1)  # 删除对应的图片
		messagebox.showerror('删除成功。', '删除成功。')
	except IndexError:
		messagebox.showerror('没有这张图片，无法删除。', '没有这张图片，无法删除。')

	label_picdisplay()


# 神经网络训练，train_btn按钮响应事件
def train():
	global batch_size_entry, max_step_entry, learning_rate_entry, train_btn, path

	Train().train(BATCH_SIZE=eval(batch_size_entry.get()), MAX_STEP=eval(max_step_entry.get()),
	              learning_rate=eval(learning_rate_entry.get()))

	messagebox.showinfo('训练完成', '训练完成。')
	train_btn['text'] = '训练完成'


# 测试神经网络，test_btn按钮响应事件
def test():
	global test_index_entry
	try:
		index = eval(test_index_entry.get())

		image = np.array(imageList[index - 1][0].resize([64, 64]))

		answer = evaluate_one_image(image)

		messagebox.showinfo('识别结果', '第{}张图片'.format(index) + answer)
	except IndexError:
		messagebox.showerror('识别照片不存在', '识别照片不存在')


# 主函数
def open_home():
	global home

	home = create_win('花卉图片分类', '450x700')  # 创建窗口

	create_label()  # 创建9个Label显示图片，默认为白色背景

	create_control()  # 加入具有添加删除等功能的框架、

	create_train()  # 创建进行训练参数设定的框架

	home.mainloop()


if __name__ == '__main__':
	login = Login()
	if (login.right):
		open_home()
	else:
		exit()
