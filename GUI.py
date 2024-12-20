from tkinter import *
import tkinter.filedialog
import tkinter.messagebox
import tkinter.ttk as ttk
import serial
import serial.tools.list_ports
import time
import IAP_Send
import threading


global ser
lock = threading.Lock()
rx_data = ""

#创建窗口
root = Tk()
root.title("IAP发送助手")
root.geometry("750x430")

#创建窗格管理
pw = PanedWindow(root, orient="horizontal",showhandle=True)
pw.pack(fill="both", expand=True)

#创建框架
fr_receive = LabelFrame(master=root,text="接收区",width=450,height=390)
fr_receive.pack(side="left",anchor="nw",fill="both",padx=5,pady=5)

fr_right = Frame(master=root,width=230,height=390)
fr_right.pack(side="right",anchor="ne",fill="both",padx=5,pady=5)

fr_port_set = LabelFrame(master=fr_right,text="串口配置",width=250, height=230)
fr_port_set.pack(side="top",anchor="nw",padx=5,pady=5,fill="x")

fr_cmd_set = LabelFrame(master=fr_right,text="命令设置",width=220, height=50)
fr_cmd_set.pack(side="top",anchor="se",padx=5,pady=5,fill="x")

fr_send = LabelFrame(master=fr_right,text="bin文件路径",width=220, height=100)
fr_send.pack(side="top",anchor="se",padx=5,pady=5,fill="both")

#拖动柄
sg = ttk.Sizegrip(master=fr_right)
sg.pack(side="bottom", anchor="se", padx=2, pady=2)

#添加框架到窗格管理
pw.add(fr_receive)
pw.add(fr_right)

#创建文本区和滚动条
text1 = Text(master=fr_receive,width=45,height=30,font=("宋体",10))
sb = Scrollbar(master=fr_receive,width=20,command=text1.yview)
# 注意顺序，先放scroll，再放text
sb.pack(side="right",fill="y")
text1.pack(side="top",padx=5,pady=5)
text1.config(yscrollcommand=sb.set)

#-----------------------------------------右侧 上边 串口配置
lb1=Label(master=fr_port_set,text="串口号")
lb2=Label(master=fr_port_set,text="波特率")
lb3=Label(master=fr_port_set,text="数据位：")
lb4=Label(master=fr_port_set,text="停止位：")
lb5=Label(master=fr_port_set,text="校验位：")
lb1.grid(row=0,column=0,padx=5,pady=5,sticky="w")
lb2.grid(row=1,column=0,padx=5,pady=5,sticky="w")
lb3.grid(row=1,column=2,padx=5,pady=5,sticky="w")
lb4.grid(row=2,column=2,padx=5,pady=5,sticky="w")
lb5.grid(row=2,column=0,padx=5,pady=5,sticky="w")

#全局变量
var_btn   = StringVar(value="打开串口")
data_len  = IntVar(value=8)
stop_len  = DoubleVar(value=1)

datalen = Entry(master=fr_port_set,textvariable=data_len,width=5)
datalen.grid(row=1,column=3,padx=5,pady=5,sticky="w")
stoplen = Entry(master=fr_port_set,textvariable=stop_len,width=5)
stoplen.grid(row=2,column=3,padx=5,pady=5,sticky="w")
#创建下拉菜单
var_cb1 = StringVar()
cb1 = ttk.Combobox(fr_port_set,textvariable=var_cb1,state="readonly", 
                   width=35)
cb1['values'] = serial.tools.list_ports.comports() #列出可用串口
cb1.current(0)  # 设置默认选项
cb1.grid(row=0,column=1,padx=5,pady=5,sticky="w",columnspan=3)

var_cb2 = IntVar()
cb2 = ttk.Combobox(fr_port_set,textvariable=var_cb2,state="readonly",width=10)
cb2['values'] = [9600,115200]
cb2.current(0)  # 设置默认选项
cb2.grid(row=1,column=1,padx=5,pady=5,sticky="w")

parity_bit = StringVar()
parity_cb = ttk.Combobox(fr_port_set,textvariable=parity_bit,state="readonly",width=10)
parity_cb['values'] = ["无","奇校验","偶校验"]
parity_cb.current(0)  # 设置默认选项
parity_cb.grid(row=2,column=1,padx=5,pady=5,sticky="w")
#-定义函数
def open_port():
    global ser
    global rx_data
    if(var_btn.get()=="打开串口"):
        try:
            ser=serial.Serial(port=cb1.get()[0:cb1.get().find(' ')],baudrate=cb2.get(),
                            bytesize=data_len.get(),
                            stopbits=stop_len.get(),timeout=0.1)
            #传递下拉框选择的参数 COM号+波特率  [0:5]表示只提取COM号字符
        except:
            tkinter.messagebox.showinfo('错误','串口打开失败')
            return
        #ser.parity   #校验位N－无校验，E－偶校验，O－奇校验
        if(parity_cb.get()=="无"):
            ser.parity=serial.PARITY_NONE#无校验
        elif parity_cb.get()=="奇校验":
            ser.parity=serial.PARITY_ODD#奇校验
        elif parity_cb.get()=="偶校验":
            ser.parity=serial.PARITY_EVEN#偶校验

        if(ser.is_open):
            var_btn.set('关闭串口')            #改变按键内容
            btn1.config(background='red')
            cb1.config(state="disabled")
            cb2.config(state="disabled")
            parity_cb.config(state="disabled")
            datalen.config(state="disabled")
            stoplen.config(state="disabled")
            rx_th=threading.Thread(target=usart_receive,name="serial_receive",daemon=True)
            rx_th.start()
        else:
            tkinter.messagebox.showinfo('错误','串口打开失败')
    elif(var_btn.get()=="关闭串口"):
        if(ser.is_open):
            ser.close()
            var_btn.set("打开串口")
            cb1.config(state="normal")
            cb2.config(state="normal")
            parity_cb.config(state="normal")
            datalen.config(state="normal")
            stoplen.config(state="normal")
            btn1.config(background=default_color)
            text1.delete(1.0,END)
            rx_data=""

def usart_receive():
    global rx_data
    rx_data=""
    while True:
        lock.acquire()
        if(ser.is_open):
            rx_buf = ser.read()
            if len(rx_buf) >0:
                time.sleep(0.01)
                rx_buf += ser.readall()  #有延迟但不易出错
                hex_data=rx_buf.hex().upper()
                if(len(hex_data)==8):
                    text1.insert(END, hex_data+'\n')
                    rx_data = "no CRC"
                elif(len(hex_data)>8):
                    str_data = str(rx_buf, encoding='utf-8')
                    text1.insert(END, str_data)
                    text1.insert(END,"\n")
                    if(begin_receive.get() in str_data):
                        rx_data = "begin ok"
                    else:
                        rx_data = "no begin"
                elif(len(hex_data)<8):
                    if(hex_data[0:2] in entry_CRC.get().upper()):
                        text1.insert(END, hex_data+'\n')
                        rx_data = "CRC ok"
                    else:
                        rx_data = "no CRC"
                text1.yview_moveto(1)
                text1.update()
        else:
            rx_data = "no ser"
            break
        lock.release()
        time.sleep(0.01)
    lock.release()

#创建按钮
btn1 = Button(fr_port_set, textvariable=var_btn,width=10,state="normal",command=open_port)
btn1.grid(row=3,column=2,padx=5,pady=5,columnspan=2)
default_color = btn1.cget('background')  # 获取默认背景颜色

#----------------------------------------右侧 中间 命令设置
begin_lb=Label(master=fr_cmd_set,text="开始升级接收到(str)")
begin_lb.grid(row=1,column=0,padx=5,pady=5,sticky="w")
CRC_lb=Label(master=fr_cmd_set,text="CRC一致接收到(HEX)")
CRC_lb.grid(row=2,column=0,padx=5,pady=5,sticky="w")
lb8=Label(master=fr_cmd_set,text="发送字节数(KB)")
lb8.grid(row=2,column=2,padx=5,pady=5,sticky="w")

#全局变量
begin_cmd = StringVar(value=":UD")
cmd_CRC_right = StringVar(value="30")
send_size = IntVar(value=1)
auto_send_begincmd = BooleanVar()
begin_receive = StringVar(value="begin")

#创建输入框
entry_begin = Entry(master=fr_cmd_set,textvariable=begin_cmd,width=8)
entry_begin.grid(row=0,column=1,padx=5,pady=5,sticky="w")
entry_CRC = Entry(master=fr_cmd_set,textvariable=cmd_CRC_right,width=8)
entry_CRC.grid(row=2,column=1,padx=5,pady=5,sticky="w")
entry_size = Entry(master=fr_cmd_set,textvariable=send_size,width=5)
entry_size.grid(row=2,column=3,padx=5,pady=5,sticky="w")
entry_begin_rx = Entry(master=fr_cmd_set,textvariable=begin_receive,width=15)
entry_begin_rx.grid(row=1,column=1,padx=5,pady=5,sticky="w",columnspan=2)

def send_begin_command():#发送:UD 开始升级命令
    send_data = entry_begin.get().strip()
    try:#字符发送
        if(ser.is_open):  #发送前判断串口状态 避免错误
            ser.write(send_data.encode('utf-8'))
            text1.insert(index=END,chars=send_data+"      ")
    except:#错误返回
        tkinter.messagebox.showinfo('错误', '发送开始失败,串口没开')

def create_auto_send_cmd():
    global rx_data
    if(auto_send_begincmd.get()):
        try:
            if(not (ser.is_open)):
                tkinter.messagebox.showinfo('错误', '串口没打开')
                return
            else:
                entry_begin.config(state="readonly")
                if(rx_data!="begin ok"):
                    text1.delete(1.0,END)
                th_auto_send = threading.Thread(target=auto_send_cmd,daemon=True)
                th_auto_send.start()
        except:
            tkinter.messagebox.showinfo('错误', '串口没打开')
            cbtn1.deselect()
    else:
        entry_begin.config(state="normal")

def auto_send_cmd():
    global rx_data
    while(rx_data!="begin ok"):
        if(auto_send_begincmd.get()==False):
            break
        else:
            lock.acquire()
            if(rx_data=="begin ok"):
                lock.release()
                break
            else:
                send_begin_command()
                rx_data=""
            lock.release()
            time.sleep(0.05)

# 创建按钮
btn6 = Button(fr_cmd_set,text="开始命令",width=10,command=send_begin_command)
btn6.grid(row=0,column=0,padx=5,pady=5,sticky="w")

#创建选择框
cbtn1 = Checkbutton(master=fr_cmd_set,text="自动发送开始命令",variable=auto_send_begincmd,
                    command=create_auto_send_cmd)
cbtn1.grid(row=0,column=2,padx=5,pady=5,columnspan=2,sticky="w")
#---------------------------------------右侧 下边 bin文件路径
#全局变量
path = StringVar(value="")
#创建输入框，选择文件
entry_path = Entry(master=fr_send,textvariable=path,width=40)
entry_path.pack(side="top",padx=5,pady=5,fill='both')

def send_data(): #发送数据
    global rx_data
    lock.acquire()
    if(entry_path.get()==""):
        tkinter.messagebox.showinfo('错误', '文件错误')
        lock.release()
        return
    lock.release()

    while(rx_data==""):
        pass

    lock.acquire()
    if(rx_data == "begin ok"):#已经开始,发送bin pack
        bin_list = IAP_Send.IAP_CRC(entry_path.get(),send_size.get()*1024)
        text1.insert(index=END,chars=f"分包、CRC校验完成,发送次数:{len(bin_list)}\n")
    else:
        tkinter.messagebox.showinfo('错误', '接收到的begin不对')
        lock.release()
        return
    
    #发送bin pack
    bin_i = 0
    retry_num = 0
    while(True):
        if(send_bin_pack(bin_list[bin_i])):
            text1.insert(index=END, chars=f"{bin_i}   ,   ")
            rx_data=""
            lock.release()
            while(rx_data==""):
                pass
            lock.acquire()
            if(rx_data=="CRC ok"):
                bin_i+=1
                retry_num=0
            elif(rx_data=="no CRC"):
                retry_num+=1
                if(retry_num>5):
                    tkinter.messagebox.showinfo('错误', '发送失败,no CRC * 5')
                    break
            elif(rx_data=="no ser"):
                tkinter.messagebox.showinfo('错误', '接收失败,串口没打开,no ser')
                break
        else:
            if(not ser.is_open):
                tkinter.messagebox.showinfo('错误', '发送失败,串口没打开,no ser')
                break
            retry_num+=1
            if(retry_num>5):
                tkinter.messagebox.showinfo('错误', '发送失败*5,重试')
                break
        if(bin_i==len(bin_list)):
            text1.insert(index=END, chars="发送完成")
            tkinter.messagebox.showinfo('成功', '发送完成')
            break
        time.sleep(0.01)
    lock.release()    

def create_thread():
    global rx_data
    try:
        if(not (ser.is_open)):
            tkinter.messagebox.showinfo('错误', '串口没打开')
            return
        else:
            if(rx_data!="begin ok"):
                text1.delete(1.0,END)
            th_send = threading.Thread(target=send_data,name="send_bin_file",daemon=True)
            th_send.start()
    except:
        tkinter.messagebox.showinfo('错误', '串口没打开')

def send_bin_pack(bin_pack):
    try:
        ser.write(bin_pack)
        return True
    except:#错误返回
        tkinter.messagebox.showinfo('错误', '发送bin pack失败')
        return False

def selectPath():
    path1 = tkinter.filedialog.askopenfilename(filetypes=[("bin文件", "*.bin")])
    if path1:
        path1 = path1.replace("/", "\\")  # 实际在代码中执行的路径为“\“ 所以替换一下
        path.set(path1)

#创建按钮
btn2 = Button(fr_send, text="选择文件",width=20,command=selectPath)
btn2.pack(side='left',anchor="center",padx=5,pady=5)
btn3 = Button(fr_send, text="开始发送",width=20,command=create_thread)
btn3.pack(side="right",anchor="center",padx=5,pady=5)

mainloop()
                

