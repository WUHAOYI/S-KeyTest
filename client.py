import socket
import time
from socket import *
import hashlib


"""
规定:
用户名长度为10-16位
验证码长度为4位
口令长度为32位
"""
address = '127.0.0.1'  # 服务器的ip地址
port = 4701
s = socket(AF_INET, SOCK_STREAM)
s.connect((address, port))
username = ""
print("请输入用户名:")

# 异或运算的逻辑
def x_o_r(byte1, byte2):
    return hex(byte1 ^ byte2)
# 客户端和服务端的交互
while True:
    msg = input()
    if msg == "exit" or not msg:
        s.close()
        break
    s.send(msg.encode("utf-8"))
    username = msg # 用户名
    # 接受服务器发送的信息，作为用户名是否已经注册的依据
    init_content = s.recv(1024).decode('utf-8')
    command = []
    # 用户名不存在的情况
    if init_content != 'exist':
        if init_content[0:8] == "initFlag":
            print("当前用户名不存在,将为您进行注册,请稍后!")
        elif init_content[0:8] == "reinFlag":
            print("当前口令已用完,将为您重新生成，请稍后!")
        seed = init_content[8:]
        content = username + seed
        # 对用户名和种子的拼接进行哈希和异或运算
        result = hashlib.md5(content.encode()).hexdigest()
        num1 = int(str(result)[0:16],16)
        num2 = int(str(result)[16:32],16)
        result = x_o_r(num1,num2)[2:]
        #print("异或运算之后的结果为:",result)
        # 生成5个口令(第1个口令提前发送到服务器端，因此只有第2-5个口令用于登录)
        for i in range(0,5):
            result = hashlib.md5(str(result).encode()).hexdigest()
            command.append(result)
        command.reverse()
        # 将第1个口令发送到服务器端
        s.send(command[0].encode("utf-8"))
        command.pop(0)
        # 将初始化完成的标志发送到服务器端
        # s.send("initFlag".encode("utf-8"))
        print('注册成功,为您生成了4条口令,请按照顺序使用')
        # file_name = "passwords/"+username+".txt"
        for i in range(0,len(command)):
            print('第'+str((i+1))+"条口令为:",command[i])

        # 一开始想用文件存储口令序列，后来放弃了该方法
        # # 向文件中记录口令
        # with open(file_name, 'w', encoding='utf-8') as f_w:
        #     for single_command in command:
        #         f_w.write(single_command+"\n")
        # f_w.close()
        print("请输入口令进行登录:")
        input_command = input()
        s.send(input_command.encode("utf-8")) # 向服务器发送口令
        login_result = s.recv(1024).decode('utf-8')
        print("口令结果为:",login_result)
        if login_result == 'success':
            print("口令正确!")
            code = s.recv(1024).decode('utf-8')
            print("生成的验证码为:", code)
            print("请输入验证码:")
            input_code = input() # 用户输入验证码
            s.send(input_code.encode("utf-8"))  # 向服务器发送验证码
            code_result = s.recv(1024).decode('utf-8')
            if code_result == 'success':
                print("登录成功!")
                # # 登录成功后需要更新文件中可用的口令
                # with open(file_name, 'r', encoding='utf-8') as f_r:
                #     lines = f_r.readlines()
                # with open(file_name, 'w', encoding='utf-8') as f_w:
                #     for line in lines:
                #         if input_command+"\n" == line:
                #             continue
                #         f_w.write(line)
                # f_r.close()
                # f_w.close()

                # 日志记录
                with open("log.txt", 'a+', encoding='utf-8') as f_log:
                    log_content = "时间:"+time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())+"\t"+"用户"+username+"进行登录,登录成功"
                    f_log.write(log_content+"\n")
                f_log.close()
                s.close()
                break
            else:
                print("验证码错误，登录失败!")
                # 日志记录
                with open("log.txt", 'a+', encoding='utf-8') as f_log:
                    log_content = "时间:"+time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())+"\t"+"用户"+username+"进行登录,由于验证码错误,登录失败"
                    f_log.write(log_content + "\n")
                f_log.close()
                s.close()
                break
        else:
            print("口令错误,登录失败!")
            # 日志记录
            with open("log.txt", 'a+', encoding='utf-8') as f_log:
                log_content = "时间:" + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()) + "\t" + "用户" + username + "进行登录,由于口令错误,登录失败"
                f_log.write(log_content + "\n")
            f_log.close()
            s.close()
            break
    # 用户名已存在的情况
    else:
        # file_name = "passwords/" + username + ".txt"
        # 首先判断当前的口令是否已经用完
        # with open(file_name, 'r', encoding='utf-8') as f_r:
        #     lines = f_r.readlines()
        #     if len(lines) == 1: # 还剩最后一条口令
        #         last_password = lines[0].strip() #最后一条数据
        #         result = last_password
        #         print("最后一条口令为:",last_password)
        #         print("下一条口令应该为:",hashlib.md5(str(last_password).encode()).hexdigest())
        #         command = []
        #         for i in range(0, 4):
        #             result = hashlib.md5(str(result).encode()).hexdigest()
        #             command.append(result)
        #         file_name = "passwords/" + username + ".txt"
        #         print(file_name)
        #         # 向文件中记录口令
        #         with open(file_name, 'w', encoding='utf-8') as f_w:
        #             for single_command in command:
        #                 f_w.write(single_command + "\n")
        #         f_w.close()
        #         print("新的口令已生成完毕!\n")

        print("当前用户名已存在,请直接输入口令进行登录:")
        input_command = input()
        s.send(input_command.encode("utf-8"))  # 向服务器发送口令
        login_result = s.recv(1024).decode('utf-8')
        if login_result == 'success':
            print("口令正确!")
            code = s.recv(1024).decode('utf-8')
            print("生成的验证码为:", code)
            print("请输入验证码:")
            input_code = input() # 用户输入验证码
            s.send(input_code.encode("utf-8"))  # 向服务器发送验证码
            code_result = s.recv(1024).decode('utf-8')
            if code_result == 'success':
                print("登录成功!")
                # # 登录成功后需要更新文件中可用的口令
                # with open(file_name, 'r', encoding='utf-8') as f_r:
                #     lines = f_r.readlines()
                # with open(file_name, 'w', encoding='utf-8') as f_w:
                #     for line in lines:
                #         if input_command+"\n" == line:
                #             continue
                #         f_w.write(line)
                # f_r.close()
                # f_w.close()

                # 日志记录
                with open("log.txt", 'a+', encoding='utf-8') as f_log:
                    log_content = "时间:"+time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())+"\t"+"用户"+username+"进行登录,登录成功"
                    f_log.write(log_content + "\n")
                f_log.close()
                s.close()
                break
            else:
                print("验证码错误，登录失败!")
                # 日志记录
                with open("log.txt", 'a+', encoding='utf-8') as f_log:
                    log_content = "时间:"+time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())+"\t"+"用户"+username+"进行登录,由于验证码错误,登录失败"
                    f_log.write(log_content + "\n")
                f_log.close()
                s.close()
                break
        else:
            print("口令错误,登录失败!")
            # 日志记录
            with open("log.txt", 'a+', encoding='utf-8') as f_log:
                log_content = "时间:" + time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()) + "\t" + "用户" + username + "进行登录,由于口令错误,登录失败"
                f_log.write(log_content + "\n")
            f_log.close()
            s.close()
            break
