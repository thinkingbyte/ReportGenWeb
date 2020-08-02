import re
import requests
from bs4 import BeautifulSoup

class DownloadAndAnalysisUtil:
    def __init__(self,productsDict,characterKeyDict,product_type):

        # 获取产品名-产品URL数据
        if len(productsDict['products'])==0:
            print("产品字典中没有产品")
            exit(0)
        #  productsList [ {'name':name，'url':url}，{'name':name，'url':url}.. ]
        self.productsList = productsDict['products']
        #  characterKeyList [ {'col1':'val1','col2':'val2'....}，{'col1':'val1','col2':'val2'....} ]
        self.characterKeyList = characterKeyDict['productItems']
        # 获取产品类型
        self.product_type = product_type


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
                return '网络有问题或者网址有误，无法解析'

            #  r.text 是str类型，r.content 是bytes类型
            # print(type(r.text),type(r.content))
            print("网页编码方式为", type(r.encoding), r.encoding)
            r.encoding = 'utf-8'
            return r.text

        except:
            print("获取当前网页失败，抓取下一个网页")
        return '网络有问题或者网址有误，无法解析'

    # 找到html 中的description介绍
    def findDescription(self,soup, index):

        # 找到网页中<meta name='description' content='..'> 其中content的内容可以作为产品的介绍部分，因为是写好的
        try:
            productDescription = soup.find('meta', attrs={"name": "description"})['content']
            self.productsList[index]['产品描述'] = productDescription
            return
            #print("get description")
            #return
        except:
            self.productsList[index]['产品描述'] = '无法在该网址中找到产品描述信息'
            #print("no description")

        try:
            productDescription = soup.find('meta', attrs={"name": "Description"})['content']
            self.productsList[index]['产品描述'] = productDescription
            #print("get Description")
            #return
        except:
            self.productsList[index]['产品描述'] = '无法在该网址中找到产品描述信息'
            #print("no Description")

    # 找到文章中的关键信息
    def findCharacter(self,divExceptLabel,index):
        if self.product_type == '录屏类软件':
            self.character_for_screen_recorder(divExceptLabel,index)
        if self.product_type == '视频剪辑类软件':
            self.character_for_video_clips(divExceptLabel,index)
        if self.product_type == '笔记类软件':
            self.character_for_take_note(divExceptLabel,index)
        if self.product_type == '单词类软件':
            self.character_for_words(divExceptLabel,index)
        if self.product_type == '会议类软件':
            self.character_for_meeting(divExceptLabel,index)

    # 筛选
    def genReport(self,divExceptLabel,index):
        if self.product_type == '录屏类软件':
            self.gen_report_for_screen_recorder(divExceptLabel,index)
        if self.product_type == '视频剪辑类软件':
            self.gen_report_for_video_clips(divExceptLabel,index)
        if self.product_type == '笔记类软件':
            self.gen_report_for_take_note(divExceptLabel, index)
        if self.product_type == '单词类软件':
            self.gen_report_for_words(divExceptLabel, index)
        if self.product_type == '会议类软件':
            self.gen_report_for_meeting(divExceptLabel, index)

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

    # 录屏软件类的产品特性筛选
    def character_for_screen_recorder(self,divExceptLabel,index):
        # TODO 需要细分再优化
        # 特征值查找
        # 开始填写characterKeysDict
        tmpDict = self.characterKeyList[index]
        tmpDict['产品名'] = self.productsList[index]['productName']

        # 检索支持平台
        for key, val in tmpDict.items():
            if key == '支持平台':
                self.find_support_platform(key, divExceptLabel, tmpDict)
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
                if '区域' in divExceptLabel or '区域录制' in divExceptLabel:
                    tmpDict[key] = '是'
            if key == '音频录制':
                # 单独音频录制
                if '音频' in divExceptLabel or '麦克风' in divExceptLabel:
                    tmpDict[key] = '是'
            if key == '画质调整':
                # 自定义原画和码特率
                if '画质调整' in divExceptLabel or '分辨率' in divExceptLabel:
                    tmpDict[key] = '是'
            if key == '鼠标特效':
                if '鼠标' in divExceptLabel:
                    tmpDict[key] = '是'
            if key == '费用':
                if 'VIP' in divExceptLabel or '会员' in divExceptLabel  or '购买'  in divExceptLabel:
                    tmpDict[key] = '付费'
        self.characterKeyList[index] = tmpDict

    # 录屏软件类的文本生成
    def gen_report_for_screen_recorder(self,divExceptLabel,index):
        # TODO 用于文章筛选的关键字， 只有包含这些关键字的语句才会被保留下来，这是改进的重点之一，需要一个和录屏软件高度相关的词库
        keyList = ['录屏', '画质', '图片', '麦克风', '录制', '录像', '特点', '音频', '视频', '水印', '鼠标', '摄像头', '功能', '色度', '抠像']

        # 开始利用关键词筛选文本库，生成文章内容
        contents = divExceptLabel.split('\n')
        # 集合结构用于去重，确定同样的一句话，只保留一份
        uniqueContents = set()

        # 以产品名作为key值
        # self.genReportData[self.characterKeyList[index]['产品名']] = []
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
                            # self.genReportData[self.characterKeyList[index]['产品名']].append(content.strip())
                            self.productsList[index]['content'].append(content.strip())
                            self.productsList[index]['content'].append('\n')

    # 视频剪辑类软件产品特性筛选
    def character_for_video_clips(self, divExceptLabel, index):
        # TODO 需要细分再优化
        # 特征值查找
        # 开始填写characterKeysDict
        tmpDict = self.characterKeyList[index]
        tmpDict['产品名'] = self.productsList[index]['productName']

        # 检索支持平台
        for key, val in tmpDict.items():
            if key == '支持平台':
                self.find_support_platform(key, divExceptLabel, tmpDict)
            if key == '4k支持':
                # 检索支持水印
                if '4k支持' in divExceptLabel:
                    tmpDict[key] = '是'
            if key == '8k支持':
                # 检索支持摄像头
                if '8k支持' in divExceptLabel:
                    tmpDict[key] = '是'
            if key == '字幕特效':
                # 区域录屏
                if '字幕' in divExceptLabel or '特效' in divExceptLabel:
                    tmpDict[key] = '是'
            if key == '画中画/分割画':
                # 单独音频录制
                if '画中画' in divExceptLabel or '分割画' in divExceptLabel:
                    tmpDict[key] = '是'
            if key == 'VR视频':
                # 自定义原画和码特率
                if 'VR' in divExceptLabel :
                    tmpDict[key] = '是'
            if key == '内容擦除':
                if '移除对象' in divExceptLabel or '移除' in divExceptLabel :
                    tmpDict[key] = '是'
            if key == '滤镜支持':
                if '滤镜' in divExceptLabel :
                    tmpDict[key] = '是'
            if key == '内置模板':
                if '模板' in divExceptLabel :
                    tmpDict[key] = '是'
        self.characterKeyList[index] = tmpDict

    # 视频剪辑类软件产品的文本生成
    def gen_report_for_video_clips(self, divExceptLabel, index):
        # TODO 用于文章筛选的关键字， 只有包含这些关键字的语句才会被保留下来，这是改进的重点之一，需要一个和录屏软件高度相关的词库
        keyList = ['产品', '视频', '特效', '滤镜', '调色', '画面', '剪辑', '水印', '视频', '水印', '音频',
                   '4K', '8K', 'VR', '字幕', '配乐',  '发布', '协作', '扩展']

        # 开始利用关键词筛选文本库，生成文章内容
        contents = divExceptLabel.split('\n')
        # 集合结构用于去重，确定同样的一句话，只保留一份
        uniqueContents = set()

        # 以产品名作为key值
        # self.genReportData[self.characterKeyList[index]['产品名']] = []
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
                            self.productsList[index]['content'].append(content.strip())
                            self.productsList[index]['content'].append('\n')

    # 笔记软件类的产品特性筛选
    def character_for_take_note(self,divExceptLabel,index):
        # TODO 需要细分再优化
        # 特征值查找
        # 开始填写characterKeysDict
        tmpDict = self.characterKeyList[index]
        tmpDict['产品名'] = self.productsList[index]['productName']

        # 检索支持平台
        for key, val in tmpDict.items():
            if key == '支持平台':
                self.find_support_platform(key,divExceptLabel,tmpDict)
            if key == 'OCR支持':
                # 检索支持水印
                if 'OCR' in divExceptLabel or 'oct' in divExceptLabel:
                    tmpDict[key] = '是'
            if key == '语音支持':
                # 检索支持摄像头
                if '语音' in divExceptLabel:
                    tmpDict[key] = '是'
            if key == '手写支持':
                # 区域录屏
                if '手写' in divExceptLabel :
                    tmpDict[key] = '是'
            if key == 'MarkDown支持':
                # 单独音频录制
                if 'MarkDown' in divExceptLabel or 'markdown' in divExceptLabel:
                    tmpDict[key] = '是'
            if key == 'office支持':
                # 自定义原画和码特率
                if 'office' in divExceptLabel or 'Office' in divExceptLabel:
                    tmpDict[key] = '是'
            if key == 'PDF支持':
                if 'PDF' in divExceptLabel:
                    tmpDict[key] = '是'
            if key == '多端同步':
                if '多端同步' in divExceptLabel :
                    tmpDict[key] = '是'
            if key == '团队协作':
                if '团队协作' in divExceptLabel :
                    tmpDict[key] = '是'
        self.characterKeyList[index] = tmpDict

    # 笔记软件类的文本生成
    def gen_report_for_take_note(self,divExceptLabel,index):
        # TODO 用于文章筛选的关键字， 只有包含这些关键字的语句才会被保留下来，这是改进的重点之一，需要一个和录屏软件高度相关的词库
        keyList = ['分享', '协作', '同步', 'OCR', '收藏', '管理', '文档', '团队', '共享', '记录', '服务',
                   '协作', '收集', '终端','手写','群组','文件夹','云端','搜索']

        # 开始利用关键词筛选文本库，生成文章内容
        contents = divExceptLabel.split('\n')
        # 集合结构用于去重，确定同样的一句话，只保留一份
        uniqueContents = set()

        # 以产品名作为key值
        # self.genReportData[self.characterKeyList[index]['产品名']] = []
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
                            # self.genReportData[self.characterKeyList[index]['产品名']].append(content.strip())
                            self.productsList[index]['content'].append(content.strip())
                            self.productsList[index]['content'].append('\n')

    # 单词类软件产品特性筛选
    def character_for_words(self, divExceptLabel, index):
        # TODO 需要细分再优化
        # 特征值查找
        # 开始填写characterKeysDict
        tmpDict = self.characterKeyList[index]
        tmpDict['产品名'] = self.productsList[index]['productName']

        # 检索支持平台
        for key, val in tmpDict.items():
            if key == '支持平台':
                self.find_support_platform(key,divExceptLabel,tmpDict)
            if key == '屏幕取词':
                # 检索支持水印
                if '屏幕取词' in divExceptLabel:
                    tmpDict[key] = '是'
            if key == '多语种':
                # 检索支持摄像头
                if '多语种' in divExceptLabel:
                    tmpDict[key] = '是'
            if key == '网络释义':
                # 区域录屏
                if '网络释义' in divExceptLabel :
                    tmpDict[key] = '是'
            if key == '音视频':
                # 单独音频录制
                if '音频' in divExceptLabel or '视频' in divExceptLabel:
                    tmpDict[key] = '是'
            if key == '打卡':
                # 自定义原画和码特率
                if '打卡' in divExceptLabel:
                    tmpDict[key] = '是'
            if key == '形象图片':
                if '形象图片' in divExceptLabel or '图片' in divExceptLabel:
                    tmpDict[key] = '是'
            if key == 'AI自适应':
                if 'AI' in divExceptLabel:
                    tmpDict[key] = '是'
            if key == '场景搭配':
                if '场景' in divExceptLabel:
                    tmpDict[key] = '是'
            if key == '词组短语':
                if '词组短语' in divExceptLabel:
                    tmpDict[key] = '是'
            if key == '闯关':
                if '闯关' in divExceptLabel:
                    tmpDict[key] = '是'
        self.characterKeyList[index] = tmpDict

        # 视频剪辑类软件产品的文本生成

    # 单词类软件产品的文本生成
    def gen_report_for_words(self, divExceptLabel, index):
        # TODO 用于文章筛选的关键字， 只有包含这些关键字的语句才会被保留下来，这是改进的重点之一，需要一个和录屏软件高度相关的词库
        keyList = ['词典','词库','词汇','词根','词缀','词表','音频','视频','语种','语言','语境','翻译','词量','词汇量','社区','实践','卡片','英语','听力','口语','场景','单词','碎片时间','语料','AI','学习','生词本','进步']

        # 开始利用关键词筛选文本库，生成文章内容
        contents = divExceptLabel.split('\n')
        # 集合结构用于去重，确定同样的一句话，只保留一份
        uniqueContents = set()

        # 以产品名作为key值
        # self.genReportData[self.characterKeyList[index]['产品名']] = []
        self.productsList[index]['content'] = []
        # 输出长度>阈值  且包含关键字的句子，切分之后会产生很多空格项目
        for content in contents:
            if len(content) >= 4:
                for key in keyList:
                    if key in content:
                        if content in uniqueContents:
                            continue
                        else:
                            # 这样处理的结果是有序的
                            uniqueContents.add(content)
                            self.productsList[index]['content'].append(content.strip())
                            self.productsList[index]['content'].append('\n')

    # 会议类软件产品特性筛选
    def character_for_meeting(self, divExceptLabel, index):
        # TODO 需要细分再优化
        # 特征值查找
        # 开始填写characterKeysDict
        tmpDict = self.characterKeyList[index]
        tmpDict['产品名'] = self.productsList[index]['productName']

        # 检索支持平台
        for key, val in tmpDict.items():
            if key == '支持平台':
                self.find_support_platform(key,divExceptLabel,tmpDict)
            if key == '考勤':
                # 检索支持水印
                if '考勤' in divExceptLabel:
                    tmpDict[key] = '是'
            if key == '视频会议':
                # 检索支持摄像头
                if '直播' in divExceptLabel:
                    tmpDict[key] = '是'
            if key == '电话接入':
                # 区域录屏
                if '电话入会' in divExceptLabel or '电话接入' in divExceptLabel:
                    tmpDict[key] = '是'
            if key == '在线文档':
                # 单独音频录制
                if '在线文档' in divExceptLabel or '在线协作' in divExceptLabel:
                    tmpDict[key] = '是'
            if key == '支持小程序':
                # 自定义原画和码特率
                if '小程序' in divExceptLabel:
                    tmpDict[key] = '是'
            if key == '云记录':
                if '云记录' in divExceptLabel :
                    tmpDict[key] = '是'
            if key == '远程屏幕控制':
                if '屏幕控制' in divExceptLabel or '远程控制' in divExceptLabel:
                    tmpDict[key] = '是'

        self.characterKeyList[index] = tmpDict

        # 视频剪辑类软件产品的文本生成

    # 会议类软件产品的文本生成
    def gen_report_for_meeting(self, divExceptLabel, index):
        # TODO 用于文章筛选的关键字， 只有包含这些关键字的语句才会被保留下来，这是改进的重点之一，需要一个和录屏软件高度相关的词库
        keyList = ['组织','效率','业务','沟通','管理','数字化','通讯录','群','信息',
                   '协作','远程','办公','会议','灵活','平台','小程序','日历','体验',
                   '语音','音频','视频','分享','文档','屏幕','文字','聊天','移动','智能','开放','安全']

        # 开始利用关键词筛选文本库，生成文章内容
        contents = divExceptLabel.split('\n')
        # 集合结构用于去重，确定同样的一句话，只保留一份
        uniqueContents = set()

        # 以产品名作为key值
        # self.genReportData[self.characterKeyList[index]['产品名']] = []
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
                            self.productsList[index]['content'].append(content.strip())
                            self.productsList[index]['content'].append('\n')

    # 确定该产品支持的平台
    def find_support_platform(self,key,divExceptLabel,tmpDict):
        if 'Win' in divExceptLabel or 'Windows' in divExceptLabel:
            tmpDict[key] += 'win '
        if 'Mac' in divExceptLabel or 'mac' in divExceptLabel:
            tmpDict[key] += 'mac '
        if '安卓' in divExceptLabel or 'Android' in divExceptLabel or 'android' in divExceptLabel:
            tmpDict[key] += 'Android '
        if 'iPad' in divExceptLabel:
            tmpDict[key] += 'iPad '
        if 'macOS' in divExceptLabel:
            tmpDict[key] += 'macOS '
        if 'App Store' in divExceptLabel or 'iPhone' in divExceptLabel:
            tmpDict[key] += 'IOS '


if __name__ == '__main__':
    pass

