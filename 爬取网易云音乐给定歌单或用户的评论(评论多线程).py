# -*- coding: UTF-8 -*-

    # 新手上路，不足之处还有很多，还望指教！
    # 这是一个简陋地获取网易云音乐某歌单或者某专辑下的所有评论，并找出某个用户(user_id)在此歌单中的
    # 所有评论然后保存在数据库中的程序。
    # 歌单id(params)、目标用户user_id，以及数据库的写入可根据自己需求更改或注释掉。
import base64
import requests
import json
import time
import random
import threading
import pymysql.cursors
from bs4 import BeautifulSoup
from Crypto.Cipher import AES


    #在mysql中创建数据库：create database netnease
    #创建表'comments'：create table comments(id int unsigned not null auto_increment primary key, music_name varchar(64), music_id int unsigned, user_name varchar(32), user_id int unsigned, comments varchar(282),page int);
    # 为了解决因emoji而出现string error时：ALTER TABLE comments CONVERT TO CHARACTER SET utf8mb4;
    
    # 连接mysql
connection = pymysql.connect(host='localhost',
                             user='root',
                             password='123321',#你的数据库密码
                             db='netease',     #连接的数据库名称
                             charset='utf8mb4',
                             port=3306,
                             cursorclass=pymysql.cursors.DictCursor)

s = requests.session()
    # 关闭默认的http connection的keep-alive
s.keep_alive = False 
    # 为了解决错误max retries exceeded whith url
requests.adapters.DEFAULT_RETRIES = 3

    # 经我摸索，每次爬取时从proxies池中使用proxies不能解决出现的403错误、nginx等问题，
    #而使用User-Agent后则不会出现错误。
user_agent_list = [
    "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
    "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0;",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
    "Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
    "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
    "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
]


user_agent = random.choice(user_agent_list)  # 随机获取代理ip
raw_headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8,en;q=0.6',
    'Cache-Control': 'no-cache',
    'Cookie':'_ntes_nnid=73794490c88b2790756a23cb36d25ec1,1507099821594; _ntes_nuid=73794490c88b2790756a23cb36d25ec1; _ngd_tid=LtmNY2JGJkw6wR3HF%2FpG2bY%2BtHhQDmOj; usertrack=c+xxC1nazueHBQJiCi7XAg==; JSESSIONID-WYYY=sJg6dw45PFKjn0VD2OuD0mzqC03xb3CnU3h4ac43kp7r9q9GJos%2BFDVyZmeGtz%5CHciN66cY5KAEW6jlHT%5COv0qzP8T3O3R5cq28%2BXJ3rc%2BkqsI4Y%2BrJIwZczDZGlvq225U%5CNWBP0iEjTnfdUG21swAhZA%5CfX29F4s9M6tz2EK7%2FESIpW%3A1507612773856; _iuqxldmzr_=32; MUSIC_U=e58d5af1daeedff199dcb9d14e06692f2db7395809fd3b393c0d6d53e13de2f484b4ab9877ef4e4ca1595168b12a45da86e425b9057634fc; __remember_me=true; __csrf=63e549f853ed105c4590d6fe622fb4f6',
    'Host': 'music.163.com',
    'Referer': 'http://music.163.com/',
    'User-Agent': user_agent
}
    # 以下encSecKey、AES_encrypt等有关解密的函数非原创，来源于知乎，
    # 参考：https://www.zhihu.com/question/36081767
    # 获取params 注意：评论每一次翻页后的的params都不一样

def get_params(first_param, forth_param):
    iv = "0102030405060708"
    first_key = forth_param
    second_key = 16 * 'F'
    h_encText = AES_encrypt(first_param, first_key.encode(), iv.encode())
    h_encText = AES_encrypt(
        h_encText.decode(), second_key.encode(), iv.encode())
    return h_encText.decode()


# 获取encSecKey
def get_encSecKey():
    encSecKey = "257348aecb5e556c066de214e531faadd1c55d814f9be95fd06d6bff9f4c7a41f831f6394d5a3fd2e3881736d94a02ca919d952872e7d0a50ebfa1769a7a62d512f5f1ca21aec60bc3819a9c3ffca5eca9a0dba6d6f7249b06f5965ecfff3695b54e1c28f3f624750ed39e7de08fc8493242e26dbc4484a01c76f739e135637c"
    return encSecKey


# AES解密
def AES_encrypt(text, key, iv):
    pad = 16 - len(text) % 16
    text = text + pad * chr(pad)
    encryptor = AES.new(key, AES.MODE_CBC, iv)
    encrypt_text = encryptor.encrypt(text.encode())
    encrypt_text = base64.b64encode(encrypt_text)
    return encrypt_text


# 获取json数据
def get_json(url, data):
    headers=raw_headers
    response = requests.post(url=url, headers=headers,data=data)
                            # proxies=proxies
    global index
    index += 1
    if index > 1500:
        index -= 1500 # 每爬取约30000条评论sleep一下
        print('每爬30000条评论,sleep几秒....ZZzzzzz......Go on')
        time.sleep(random.randint(1, 3))

    return response.content


# 传入post数据
def crypt_api(id, offset):
    url = "http://music.163.com/weapi/v1/resource/comments/R_SO_4_%s/?csrf_token=" % id
    first_param = "{rid:\"\", offset:\"%s\", total:\"true\", limit:\"20\", csrf_token:\"\"}" % offset
    forth_param = "0CoJUm6Qyw8W8jud"
    params = get_params(first_param, forth_param)
    encSecKey = get_encSecKey()
    data = {
        "params": params,
        "encSecKey": encSecKey
    }
    return url, data

###################################################################################################################


# 获取评论
def get_the_first_half_comment(id,comments_sum,music_name):
    raw_page = 0 #用于获得目标用户评论所在的页数
    for i in range(0, comments_sum//2, 20):  # 每一页有20条评论
        #proxies = random.choice(proxy_pool)  # 随机获取代理ip
        # 对于每一页需请求一次，使用一次代理
        offset = i
        url, data = crypt_api(id, offset)
        json_text = get_json(url, data) 
        json_dict = json.loads(json_text.decode("utf-8"))
        json_comment = json_dict['comments']
        for comment in json_comment:
        # 每一个comment均为包含一个user的所有评论信息
        # 找了只有一条评论的歌曲信息，comment格式如下：
        # music_id:5283862 music_name:忘了我吧!我的最爱
        #{"isMusician":false,"userId":-1,"topComments":[],"moreHot":false,"hotComments":[],"code":200,
        #"comments":[{"user":{"locationInfo":null,"experts":null,"authStatus":0,"remarkName":null,"avatarUrl":"http://p1.music.126.net/8N882UcPox32hcrYCpfOxw==/19083123811686650.jpg","userId":429847262,"expertTags":null,"vipType":0,"nickname":"故事偷盗者","userType":0},
        #"beReplied":[],"likedCount":0,"liked":false,"commentId":321330017,"time":1488441683356,"content":"为了遮羞才把书包挡住屁股给你学牛看，从此每天乐此不疲逗你开心。你初一的时候开始不好好学习，谈了男朋友，最后跟他私奔，现在都还杳无音讯！但不管怎样，我都希望你现在能像以前一样，找到那头可以逗你哈哈大笑的牛，幸福下去。晚安[牵手]",
        #"isRemoveHotComment":false}],"total":1,"more":false}
            user_id = comment['user']['userId']
             # 如果该歌曲中的评论有目标用户(user_id)则把目标用户的评论信息保存到数据库
            if user_id == 48353:    #网易UFO丁磊
                user_name = comment['user']['nickname']
                comment = comment['content']
                print(music_name, '——', ':', comment)
                # page 是目标评论所在位置：最后一页为-1,倒数第二页为-2....
                page=-(comments_sum // 20 + 1 - raw_page)
                #print(page)
                # 添加目标用户评论的相关信息到到数据库中
                with connection.cursor() as cursor:
                    sql = "INSERT INTO `comments` ( `user_name`,`comments`,`music_name`,`music_id`,`page`) VALUES (%s,%s,%s,%s,%s)"
                    cursor.execute(sql, (user_name,
                        comment, music_name, id,page))
                connection.commit() #提交数据库的更改

        raw_page += 1    



def get_the_second_half_comment(id,comments_sum,music_name):
    raw_page = 0 
    half_page=0
    for the_back_half_num in range(0, comments_sum//2, 20):
        half_page+=1
        pass

    for i in range(the_back_half_num+20,comments_sum,20):
        offset = i
        url, data = crypt_api(id, offset)
        json_text = get_json(url, data) 
        json_dict = json.loads(json_text.decode("utf-8"))
        json_comment = json_dict['comments']
        for comment in json_comment:
            user_id = comment['user']['userId']
            if user_id == 48353:    #网易UFO丁磊
                user_name = comment['user']['nickname']
                comment = comment['content']
                page=-(comments_sum // 20 + 1 - raw_page)+half_page
                print('《'+str(music_name)+'》'+'——'+':', comment,page)
                #print(page)
                with connection.cursor() as cursor:
                    sql = "INSERT INTO `comments` ( `user_name`,`comments`,`music_name`,`music_id`,`page`) VALUES (%s,%s,%s,%s,%s)"
                    cursor.execute(sql, (user_name,
                        comment, music_name, id,page))
                connection.commit() #提交数据库的更改

        raw_page += 1   


# 用本地文档生成随机proxies
#raw_proxy_pool = []
#with open("/home/hardly/文档/proxy.txt")as fin:
    #for line in fin.readlines():
        #line = line.strip("\n")
        #pro = {'https': 'https:' + line}
        # print(proxies)
        #raw_proxy_pool.append(pro)

# 获取专辑对应的页面
# 获取专辑或者歌单对应的页面 (相应改为album 或 playlist)


index = 0 # 用于每爬取1500页(30000条评论)sleep一下

def get_music_info():
    num = 0 # 计量爬行总评论数
    params = {'id': 907742221}
    r = requests.get('http://music.163.com/playlist',params=params,headers=raw_headers)
    #proxies=random.choice(raw_proxy_pool)

    soup = BeautifulSoup(r.content.decode(), 'html.parser')
    body = soup.body
    musics = body.find('ul', attrs={'class': 'f-hide'}).find_all('li')  # 获取专辑的所有音乐
    for music in musics:  # 对于包含歌曲的musics，解析获得其相应的music_id和music_name
        music = music.find('a')
        music_id = music['href'].replace('/song?id=', '')
        music_name = music.getText()
        song_name = music_name
        try:
            offset = 0
            url, data = crypt_api(music_id, offset)  # return url, data
            json_text = get_json(url, data)
            # json_dict为得到包含所有评论的dict
            json_dict = json.loads(json_text.decode("utf-8"))
            comments_sum = json_dict['total']  # 评论总数
            print('《'+str(music_name)+'》'+'共有:{}条评论,正在爬取........'.format(comments_sum))
            num += comments_sum # 将所有的comments_sum累加便是爬取总评论数
            raw_page = 0 #用于获得目标用户评论所在的页数   

            threads = []
            t1= threading.Thread(target=get_the_first_half_comment, args=(music_id,comments_sum,music_name))
            threads.append(t1)
            t2= threading.Thread(target=get_the_second_half_comment, args=(music_id,comments_sum,music_name))
            threads.append(t2)
            for t in threads:
                t.start()
            for t in threads:
                t.join()
            print('目前共成功爬取:'+str(num)+'条评论')
            time.sleep(random.randint(1, 3))
        except Exception as e:
            print('出现错误:', e)

if __name__ == '__main__':
    get_music_info()
