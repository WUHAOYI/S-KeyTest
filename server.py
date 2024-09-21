import random
import string
from socket import *
import threading
import hashlib

address='127.0.0.1'
port=4701
buffsize=1024
s = socket(AF_INET, SOCK_STREAM)
s.bind((address,port))
s.listen(20)     #最大连接数
usernameDic = {}
initFlagDic = {} #记录当前可用的口令条数
code = ""

# 需要生成口令的标志
def get_init_content(flag):
    # 生成种子
    seeds_s = string.digits
    random_str_s = []
    for i in range(0, 6):
        random_str_s.append(random.choice(seeds_s))
    seed = "".join(random_str_s)
    # 通过flag判断是第一次注册还是重新生成口令
    if flag == 0:
        init_content = "initFlag" + seed
    if flag == 1:
        init_content = "reinFlag" + seed
    return init_content

# tcp连接
def tcplink(sockdata,address):
    global code
    while True:
        try:
            res = sockdata.recv(buffsize).decode('utf-8')
            # print("当前发送过来的数据为:",res)
            if res == "exit" or not res:
                print('客户端已下线:', address)
                print("-------------------------------")
                break
            # 处理口令
            if len(res) == 32:
                user_input = res
                # 说明要用新的一组口令，之前的那一条口令失效
                if initFlagDic[username] == 0:
                    usernameDic[username] = ''
                password_now = usernameDic.get(username)
                print("当前密码为:",password_now)
                if password_now == '': #说明此时第一条口令还没有发送过来
                    usernameDic[username] = user_input
                    initFlagDic[username] = 4
                    print("成功在服务器中添加密码:",user_input)
                else: #说明此时需要验证口令
                    print("存储口令为:",password_now)
                    print("用户输入的口令为:",user_input)
                    # 当前存储的口令是由用户应当输入的口令进行一次md5哈希得来的
                    if str(hashlib.md5(str(user_input).encode()).hexdigest()) == str(password_now):
                        sockdata.send('success'.encode('utf-8'))
                        usernameDic[username] = user_input #更新此时的口令
                        initFlagDic[username] = initFlagDic.get(username) - 1 #更新可用的口令条数
                        print("更新后的密码为:",user_input)
                        # 向客户端发送验证码
                        seeds = string.digits
                        random_str = []
                        for i in range(0,4):
                            random_str.append(random.choice(seeds))
                        code = "".join(random_str)
                        print("生成的验证码为:",code)
                        sockdata.send(code.encode('utf-8'))
                    else:
                        sockdata.send('fail'.encode('utf-8'))
            # 处理验证码
            if len(res) == 4:
                code_input = res
                print("当前验证码为:",code)
                print("用户输入的验证码为:",code_input)
                if code_input == code:
                    # 用户登录成功的标志，需要更新可用口令条数
                    sockdata.send('success'.encode('utf-8'))

                else:
                    sockdata.send('fail'.encode('utf-8'))
            # 处理用户名 向客户端发送种子seed
            if 10 <= len(res) <= 16 :
                username = res
                # 用户名不存在
                if not (res in usernameDic.keys()):
                    usernameDic[username] = ''
                    initFlagDic[username] = 0
                    # 发送初始化标志和种子
                    sockdata.send(get_init_content(0).encode("utf-8"))
                else:
                    # 用户名存在
                    # 口令已经用完，需要重新生成口令
                    if initFlagDic[username] == 0:
                        sockdata.send(get_init_content(1).encode("utf-8"))
                    else:
                        sockdata.send('exist'.encode('utf-8'))
            # 初始化的标志
            # if res == "initFlag":

        except:
            sockdata.close()
            print('客户端已下线:',address)
            print("-------------------------------")
            break

# 线程
def receiveFromClient():
    while True:
        clientsock, clientaddress = s.accept()
        print('客户端已连接:', clientaddress)
        t=threading.Thread(target=tcplink,args=(clientsock,clientaddress))
        t.start()

if __name__ == '__main__':
    t1 = threading.Thread(target=receiveFromClient, args=())
    t1.start()