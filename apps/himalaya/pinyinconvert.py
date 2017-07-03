# coding=utf-8
import re
import sys


reload(sys)
sys.setdefaultencoding('utf-8')

def convert(ch):
    """该函数通过输入汉字返回其拼音，如果输入多个汉字，则返回第一个汉字拼音.
       如果输入数字字符串，或者输入英文字母，则返回其本身(英文字母如果为大写，转化为小写)
    """
    length = len('柯')  # 测试汉字占用字节数，utf-8，汉字占用3字节.bg2312，汉字占用2字节
    intord = ord(ch[0:1])
    if (intord >= 48 and intord <= 57):
        return ch[0:1]
    if (intord >= 65 and intord <= 90) or (intord >= 97 and intord <= 122):
        return ch[0:1].lower()
    ch = ch[0:length] #多个汉字只获取第一个
    with open(r'hanzi') as f:
        for line in f:
            if ch in line:
                return line[length:len(line)-2]


def hanzi(str):
    # print 'hanzi'
    # str='成g都nedafs个'
    str=str.decode('utf8')
    # print (str)
    zhPattern = re.compile(ur'[\u4e00-\u9fa5]')
    chlist=zhPattern.findall(str)
    pinyin=''
    num=0
    for item in chlist:
        # print (item)
        # print convert(item)
        if num==0:
            itempinyin=convert(item)[0].upper()+convert(item)[1:]
        else:
            itempinyin = convert(item)
        pinyin=pinyin+itempinyin
        num+=1
    return pinyin


# if __name__ == '__main__':
#     print 'main'
#     str=' 西安'
#     pinyin=hanzi(str)
#     print (pinyin)

