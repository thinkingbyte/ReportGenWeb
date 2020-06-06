import re
import requests
from bs4 import BeautifulSoup

class DownloadAndAnalysisUtil:
    def __init__(self,productsDict,characterKeyDict):
        # 获取产品名-产品URL数据
        if len(productsDict['products'])==0:
            print("产品字典中没有产品")
            exit(0)
        #  productsList [ {'name':name，'url':url}，{'name':name，'url':url}.. ]
        self.productsList = productsDict['products']
        #  productsList [ {'col1':'val1','col2':'val2'....}，{'col1':'val1','col2':'val2'....} ]
        self.characterKeyList = characterKeyDict['productItems']


    def downloadHTML(self,index):
        # 浏览器伪装
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'
        }
        # 目标产品url下载
        try:
            # 抓取第i个产品的url
            r = requests.get(self.productsList[index]['url'], headers=header)
            print("搜索网址为", r.url)
            print("HTTP响应码为（200表示成功响应）", r.status_code)

            # 获取页面失败
            if r.status_code != 200:
                print("响应非200，抓取下一个页面")

            #  r.text 是str类型，r.content 是bytes类型
            # print(type(r.text),type(r.content))
            print("网页编码方式为", type(r.encoding), r.encoding)
            r.encoding = 'utf-8'
            return r.text

        except:
            print("获取当前网页失败，抓取下一个网页")
        return ''

    # 找到html 中的description介绍
    def findDescription(self,soup, index):
        # 找到网页中<meta name='description' content='..'> 其中content的内容可以作为产品的介绍部分，因为是写好的
        try:
            productDescription = soup.find('meta', attrs={"name": "description"})['content']
            self.productsList[index]['产品描述'] = productDescription
            #print("get description")
            #return
        except:
            pass
            #print("no description")

        try:
            productDescription = soup.find('meta', attrs={"name": "Description"})['content']
            self.productsList[index]['产品描述'] = productDescription
            #print("get Description")
            #return
        except:
            pass
            #print("no Description")

    # 找到文章中的关键信息
    def findCharacter(self,divExceptLabel,index):
        # TODO 需要细分再优化
        # 特征值查找
        # 开始填写characterKeysDict
        tmpDict = self.characterKeyList[index]
        tmpDict['产品名'] = self.productsList[index]['productName']
        # 检索支持平台
        for key,val in tmpDict.items():
            if key=='支持平台':
                if 'Win' or 'Windows' in divExceptLabel:
                    tmpDict[key] += 'win '
                if 'Mac' or 'mac' in divExceptLabel:
                    tmpDict[key] += 'mac '
                if '安卓' or 'Android' or 'android' in divExceptLabel:
                    tmpDict[key] += 'Android'
            if key == '水印':
                # 检索支持水印
                if '水印' in divExceptLabel:
                    tmpDict[key] = '是'
            if key == '摄像头桌面组合录制':
                # 检索支持摄像头
                if '摄像头' in divExceptLabel:
                    tmpDict[key] = '是'
            if key == '区域录制':
                # 区域录屏
                if '区域' or '区域录制' in divExceptLabel:
                    tmpDict[key] = '是'
            if key == '音频录制':
                # 单独音频录制
                if '音频' or '麦克风' in divExceptLabel:
                    tmpDict[key] = '是'
            if key == '画质调整':
                # 自定义原画和码特率
                if '音频' or '麦克风' in divExceptLabel:
                    tmpDict[key] = '是'
            if key == '鼠标特效':
                if '鼠标' in divExceptLabel:
                    tmpDict[key] = '是'
            if key == '费用':
                if 'VIP' or '会员' or '购买' in divExceptLabel:
                    tmpDict[key] = '付费'
        self.characterKeyList[index] = tmpDict

    # 筛选
    def genReport(self,divExceptLabel,index):
        # TODO 用于文章筛选的关键字， 只有包含这些关键字的语句才会被保留下来，这是改进的重点之一，需要一个和录屏软件高度相关的词库
        keyList = ['录屏', '画质','图片','麦克风','录制', '录像', '特点','音频', '视频','水印','鼠标','摄像头','功能','色度','抠像']

        # 开始利用关键词筛选文本库，生成文章内容
        contents = divExceptLabel.split('\n')
        # 集合结构用于去重，确定同样的一句话，只保留一份
        uniqueContents = set()

        # 以产品名作为key值
        #self.genReportData[self.characterKeyList[index]['产品名']] = []
        self.productsList[index]['content'] = []
        # 输出长度>阈值  且包含关键字的句子，切分之后会产生很多空格项目
        for content in contents:
            if len(content) >= 10:
                for key in keyList:
                    if key in content:
                        if content in uniqueContents:
                            continue
                        else:
                            # 这样处理的结果是有序的
                            uniqueContents.add(content)
                            #self.genReportData[self.characterKeyList[index]['产品名']].append(content.strip())
                            self.productsList[index]['content'].append(content.strip())
                            # print(repr(content))
                            # print('*' * 10)

    # 函数解释： 从URL下载网页，提取文字信息，筛选提炼成文，同时找出该产品是否有给出的特性
    def analysisFromDict(self):
        # 循环抓取需要抓取的网页页面 也就是前端输入的产品--产品URL对数
        # 需要抓取的页面数目
        count = len(self.productsList)

        for index in range(count):
            # 下载网页
            strHTML = self.downloadHTML(index)
            # 先找到body中的所有div ，然后提取出div中的文字。这样可以减少工作量
            soup = BeautifulSoup(strHTML, "lxml")
            # 寻找并且设置description
            self.findDescription(soup,index)

            # 使用body标签内容新建soup对象
            body = soup.find('body')
            soup1 = BeautifulSoup(str(body), 'lxml')

            # 去除HTML标签
            divExceptLabel = re.sub('<[^>]+>', '', soup1.text)
            #print(divExceptLabel)

            #  检查文本，查看是否出现要寻找的特征 ，eg，文章中出现支持windows下载，则说明该产品支持win系统
            self.findCharacter(divExceptLabel,index)

            # 生成文本内容
            self.genReport(divExceptLabel,index)

        return self.productsList,self.characterKeyList


if __name__ == '__main__':
    pass

