# coding=UTF-8

import asyncio
import re
import base64


import execjs
from aiohttp_requests import requests
from lxml import etree


HOST = "http://shaoq.com:7777/"
MAIN_PAGE_URL = f"{HOST}exam"

async def req():
    # 跳转页请求
    resp = await requests.get(MAIN_PAGE_URL)
    resp_text = await resp.text()

    # 取出图片url并请求
    image_urls = [f"{HOST}{image.get('src')}"for image in etree.HTML(resp_text).xpath("//img")]
    await asyncio.gather(*[requests.get(image_url)for image_url in image_urls])

    # 拿到内容页
    respl = await requests.get(MAIN_PAGE_URL)
    respl_text = await respl.text()

    doc = etree.HTML(respl_text)


    # 调用JS生成CSS
    with open("E:/test1/exam.js",'r',encoding='utf-8')as fe:
        ajs = fe.read()

    js = execjs.compile(ajs)
    css = base64.b64decode(js.call("get_css",respl_text)).decode()
    # print(css)

    #解析css并覆盖到span标签的text中
    css_dict = css2dict(css)
    # print(css_dict)
    spans = doc.xpath('//span')
    for span in spans:
        span.text = eval(css_dict.get(span.get("class")))
        # print(span.text)

    #移除p和script标签
    for bad in doc.xpath("//body/p|//body/script"):
        bad.getparent().remove(bad)

    #用xpath直接取出body下的所有text，在清楚前后空格和换行符之后并合并到同一个字符串
    exam_text = "".join([text.strip() for text in doc.xpath('//body//text()')])
    print(exam_text)

def css2dict(css):
    return dict(re.findall(r'\.([\s\S]*?)::before {content:([\s\S]*?);}',css))

if __name__ =="__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(req())