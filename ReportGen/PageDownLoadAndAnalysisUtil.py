import re
import requests
from bs4 import BeautifulSoup

class DownloadAndAnalysisUtil:
    def __init__(self,productsDict,characterKeyDict):
        # 获取产品名-产品URL数据
        if len(productsDict['products'])==0:
            print("产品字典中没有产品")
            exit(0)
        #  productsList [ {name，url}，{name，url}.. ]
        self.productsList = productsDict['products']
        self.characterKeyList = characterKeyDict['productItems']
        # 用来存放对产品名，产品描述
        self.genReportData = {}


    def downloadHTML(self,index):
        header = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36'
        }
        # 目标产品url下载
        try:
            # 抓取第i个产品的url
            r = requests.get(self.productsList[index]['url'], headers=header)
            print("搜索网址为", r.url)
            print("HTTP响应码为（200表示成功响应）", r.status_code)
        except:
            print("获取当前网页失败，抓取下一个网页")

        # 获取页面失败
        if r.status_code != 200:
            print("响应非200，抓取下一个页面")


        #  r.text 是str类型，r.content 是bytes类型
        # print(type(r.text),type(r.content))
        print("网页编码方式为", type(r.encoding), r.encoding)
        r.encoding = 'utf-8'
        return r.text

    def findDescription(self,soup, index):
        # 找到网页中<meta name='description' content='..'> 其中content的内容可以作为产品的介绍部分，因为是写好的
        try:
            productDescription = soup.find('meta', attrs={"name": "description"})['content']
            self.characterKeyList[index]['产品描述'] = productDescription
            print("get description")
            #return
        except:
            print("no description")

        try:
            productDescription = soup.find('meta', attrs={"name": "Description"})['content']
            self.characterKeyList[index]['产品描述'] = productDescription
            print("get Description")
            #return
        except:
            print("no Description")

    def findCharacter(self,divExceptLabel,index):
        # TODO 这也是一个需要改进的地方
        # 特征值查找
        # 开始填写characterKeysDict
        self.characterKeyList[index]['产品名'] = self.productsList[index]['productName']
        # 检索支持平台
        if 'Win' or 'Windows' in divExceptLabel:
            self.characterKeyList[index]['支持平台'] += 'win '
        if 'Mac' or 'mac' in divExceptLabel:
            self.characterKeyList[index]['支持平台'] += 'mac '
        if '安卓' or 'Android' or 'android' in divExceptLabel:
            self.characterKeyList[index]['支持平台'] += 'Android'

        # 检索支持水印
        if '水印' in divExceptLabel:
            self.characterKeyList[index]['支持水印'] = '是'
        # 摄像头桌面组合录制
        if '摄像头' in divExceptLabel:
            self.characterKeyList[index]['摄像头桌面组合录制'] = '是'
        # 区域录屏
        if '区域' or '区域录制' in divExceptLabel:
            self.characterKeyList[index]['区域录制'] = '是'
        # 单独音频录制
        if '音频' or '麦克风' in divExceptLabel:
            self.characterKeyList[index]['音频录制'] = '是'
        # 自定义原画和码特率
        if '音频' or '麦克风' in divExceptLabel:
            self.characterKeyList[index]['画质调整'] = '是'
        if '鼠标' in divExceptLabel:
            self.characterKeyList[index]['鼠标特效'] = '是'
        if 'VIP' or '会员' or '购买' in divExceptLabel:
            self.characterKeyList[index]['费用'] = '付费'

    def genReport(self,divExceptLabel,index):
        # TODO 用于文章筛选的关键字， 只有包含这些关键字的语句才会被保留下来，这是后期改进的重点之一
        keyList = ['录屏', '画质','图片','麦克风','录制', '录像', '特点','音频', '视频','水印','鼠标','摄像头','功能','色度','抠像']

        # 开始利用关键词筛选文本库，生成文章内容
        contents = divExceptLabel.split('\n')
        # 集合结构用于去重，确定同样的一句话，只保留一份
        uniqueContents = set()

        # 以产品名作为key值
        self.genReportData[self.characterKeyList[index]['产品名']] = []
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
                            self.genReportData[self.characterKeyList[index]['产品名']].append(content.strip())
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
            #TODO 选择一张图片下载，作为演示图  现阶段可以后期手工贴图
            #allImages = soup1.find_all('img')

            # 去除标签
            divExceptLabel = re.sub('<[^>]+>', '', soup1.text)
            #print(divExceptLabel)

            #  检查文本，查看是否出现要寻找的特征 ，eg，文章中出现支持windows下载，则说明该产品支持win系统
            self.findCharacter(divExceptLabel,index)

            # 生成文本内容
            self.genReport(divExceptLabel,index)

        return self.genReportData,self.characterKeyList


if __name__ == '__main__':

    # 假设这是用户的输入
    productDict = {
        'products':[
            {'productName': 'Bandicam班迪录屏','url':'https://www.bandicam.cn/screen-recorder/'},
            {'productName': 'EV录屏','url':'https://www.ieway.cn/evcapture.html'},
            {'productName': '嗨格式录屏大师','url':'http://www.higeshi.com/lupingdashi'},
            {'productName': '迅捷屏幕录像工具', 'url': 'https://rj.cjxz.com/recordingscreen4/'},
        ]
    }

    characterDictCopyDefault = {
        '产品名': ' ', '产品描述': ' ', '支持平台': ' ', '支持水印': ' ',
        '摄像头桌面组合录制': ' ', '区域录制': ' ', '音频录制': ' ', '画质调整': ' ',
        '鼠标特效': ' ', '费用': ' ', '下载链接': ' '
    }

    # 有几个产品条目输入，就在checkKeysDict 新增一个characterDictCopyDefault  就是一个表格的行
    characterKeysDict = {'productItems': []}
    for i in range(4):
        dictCopy = characterDictCopyDefault.copy()
        characterKeysDict['productItems'].append(dictCopy)

    # 这是一些产品的特性，我们去爬取下来的文字中去检索是否有这些信息。
    # checkKeysDict={
    #     'productItems':[
    #         # 产品1
    #         {'productName':'','description':'','supportPlatform':'','supportWarterMark':'','supportCameraAndDesktop':'','supportPartArea':'',
    #          'supportAudio':'','supportImageQualityAdjust':'','supportMouseEffect':'','PayOrFree':'','downloadLink':''},
    #         # 产品2
    #         {'productName': '', 'description':'','supportPlatform': '', 'supportWarterMark': '', 'supportCameraAndDesktop': '',
    #          'supportPartArea': '','supportAudio': '', 'supportImageQualityAdjust': '', 'supportMouseEffect': '', 'PayOrFree': '',
    #          'downloadLink': ''},
    #         # 产品3
    #         {'productName': '', 'description':'','supportPlatform': '', 'supportWarterMark': '', 'supportCameraAndDesktop': '',
    #          'supportPartArea': '',
    #          'supportAudio': '', 'supportImageQualityAdjust': '', 'supportMouseEffect': '', 'PayOrFree': '',
    #          'downloadLink': ''}
    #     ]
    # }

    # characterKeysDict = {'productItems': [
    #     # 产品1
    #     {
    #         '产品名': ' ', '产品描述': ' ', '支持平台': ' ', '支持水印': ' ',
    #         '摄像头桌面组合录制': ' ', '区域录制': ' ', '音频录制': ' ', '画质调整': ' ',
    #         '鼠标特效': ' ', '免费/收费': ' ', '下载链接': ' '
    #     },
    #     # 产品2
    #     {
    #         '产品名': ' ', '产品描述': ' ', '支持平台': ' ', '支持水印': ' ',
    #         '摄像头桌面组合录制': ' ', '区域录制': ' ', '音频录制': ' ', '画质调整': ' ',
    #         '鼠标特效': ' ', '免费/收费': ' ', '下载链接': ' '
    #     },
    #     # 产品3
    #     {
    #         '产品名': ' ', '产品描述': ' ', '支持平台': ' ', '支持水印': ' ',
    #         '摄像头桌面组合录制': ' ', '区域录制': ' ', '音频录制': ' ', '画质调整': ' ',
    #         '鼠标特效': ' ', '免费/收费': ' ', '下载链接': ' '
    #     },
    #     # 产品4
    #     {
    #         '产品名': ' ', '产品描述': ' ', '支持平台': ' ', '支持水印': ' ',
    #         '摄像头桌面组合录制': ' ', '区域录制': ' ', '音频录制': ' ', '画质调整': ' ',
    #         '鼠标特效': ' ', '免费/收费': ' ', '下载链接': ' '
    #     }
    # ]}

    downloader = DownloadAndAnalysisUtil(productDict,characterKeysDict)
    genReportData,tableValue = downloader.analysisFromDict()
    print(genReportData)
    print()
    print(tableValue)

    #keys = genReportData.keys()

    # for key in keys:
    #     for data in genReportData[key]:
    #         print(str(data).strip())
    #print(genReportData)
