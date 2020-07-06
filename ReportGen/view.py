'''
这是自己创建的视图文件
'''

from django.http import HttpResponse
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from product.models import Product
from ReportGen.ScreenCutUtil import ScreenCut
from ReportGen.PageDownLoadAndAnalysisUtil import DownloadAndAnalysisUtil
import os


def index(request):
    return render(request,"index.html")

def getResult(request):
    # 用户输入的产品和产品对应的官网 productNameAndUrlDict ：   {"products": [{name,url}，{name,url}...]}
    productNameAndUrlDict = {"products": []}
    productCharactorString = []
    userInputCharactor = False
    try:
        # 收到的产品条目数量为
        numberOfRow = request.POST['numberOfRow']
        print('后台-收到的产品条目数量为：', type(numberOfRow), numberOfRow)

        # 产品的类型是
        product_type = request.POST['product_type_input']
        print('产品的类型是：', type(product_type), product_type)

        # 用户输入的产品特性-用于做表格对比
        productCharacter = request.POST['characters']
        productCharactorString = productCharacter.strip().split()
        # 用户输入产品特性需要大于3 否则使用默认产品特性
        if len(productCharactorString) > 3:
            userInputCharactor = True
        print('后台-用户输入的产品特性为：', type(productCharacter), productCharactorString)



        # 产品字典
        count = int(numberOfRow)
        for i in range(count):
            productName = 'product'+str(i+1)
            productURLName = 'productUrl'+str(i+1)
            print(productName,productURLName)
            print('后台：',request.POST[productName],request.POST[productURLName])
            productNameAndUrlDict['products'].append({'productName': request.POST[productName], 'url': request.POST[productURLName]})

    except:
        contents = {'failed': '产品网址有误或者网络出现问题'}
        print("读取数据失败")
        return render(request, 'error.html', contents)


    ###########################################################################################################################
    # 爬虫处理的部分

    #这是默认产品的特性，我们去爬取下来的文字中去检索是否有这些信息
    #一个产品的特性副本
    # characterDictCopyDefault = {
    #         'productName': ' ', 'description': ' ', 'supportPlatform': ' ', 'supportWarterMark': '否',
    #         'supportCameraAndDesktop': '否', 'supportPartArea': '否','supportAudio': '否', 'supportImageQualityAdjust': '否',
    #         'supportMouseEffect': ' ', 'PayOrFree': ' ','downloadLink': ' '}



    # 这是一个产品默认特性字典模板

    # 获取内置产品描述类，通过用户输入的产品类型
    try:
        productInner = Product.objects.get(type_name=product_type)
    except ObjectDoesNotExist:
        # 产品类型内置不存在
        contents = {'failed': "本项目暂时不支持该类产品的调研报告生成"}
        print("数据库中未存储该类型的产品数据")
        return render(request, 'error.html', contents)


    product_character = productInner.product_character
    product_preface = productInner.product_preface
    product_closing = productInner.product_closing

    result = {}
    result['product_preface'] = product_preface
    result['product_closing'] = product_closing


    # characterDictCopyDefault = {
    #     '产品名': ' ', '支持平台': ' ', '支持水印': '否',
    #     '摄像头桌面组合录制': '否', '区域录制': '否', '音频录制': '否', '画质调整': '否',
    #     '鼠标特效': '否', '费用': '付费'}

    # 内置的产品特性
    characterDictCopyDefault = {'产品名': ' '}
    for item in product_character.split('，'):
        if item == '支持平台':
            characterDictCopyDefault[item] = ''
        else:
            characterDictCopyDefault[item] = '否'

    # TODO  characterDictCopy 这个其实是可以由用户本身来确定的，比如用户输入声音录制，桌面摄像头组合录制，鼠标移动特效等
    # 类比于上面的 characterDictCopyDefault
    characterDictCopyUser = {
        '产品名': ' '
    }

    # 如果是用户自定义特性，产生一个对比特性字典
    if userInputCharactor:
        for item in  productCharactorString:
            characterDictCopyUser[item]='否'
        print(characterDictCopyUser)

    # 有几个产品条目输入，就在checkKeysDict 新增一个characterDictCopyDefault  就是一个表格的行
    characterKeysDict = {'productItems': []}
    for i in range(int(numberOfRow)):
        if userInputCharactor:
            dictCopy = characterDictCopyUser.copy()
        else:
            dictCopy = characterDictCopyDefault.copy()
        characterKeysDict['productItems'].append(dictCopy)

    #  初始化一个内容解析器 并
    analysisUtil = DownloadAndAnalysisUtil(productNameAndUrlDict,characterKeysDict,productInner.type_name)

    # 调用内容解析函数，返回每个产品的介绍和表格的内容, 传入的参数是用于描述表格的行，
    # productValue  [ {产品名，产品简介，产品内容} {...} {...}]
    # tableValue  键-值(列表（字典）)
    productValue,tableValue = analysisUtil.analysisFromDict()

    # result字典数据，传回前端，用于HTML展示
    result['products'] = productValue
    result['tables'] = tableValue
    result['tableKey'] = tableValue[0].keys()

    # 如果该目标url的截图尚未获取过，则获取页面截图
    cutPicNameList = os.listdir("D:\\PycharmProjects\\ReportGenWeb\\static\\image")
    for productDict in productNameAndUrlDict["products"]:
        if productDict["productName"]+".jpg" not in cutPicNameList:
            # 去获取屏幕截图
            screenCut = ScreenCut(productDict["url"], productDict["productName"])
            screenCut.cutScreen()
        else:
            pass
            #print(productDict["productName"]+"截图已经缓存")

    return render(request, 'index.html', result)






