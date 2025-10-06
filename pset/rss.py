import requests
import xml.etree.ElementTree as ET

def buildQA():
  question = '我的博客的最新一期博文标题是什么?'
  correct_answer = ''

  url = "https://zelikk.blogspot.com/rss.xml"

  # 请求 RSS 数据
  response = requests.get(url)

  # 解析 XML
  root = ET.fromstring(response.content)

  # RSS 结构一般是 <rss><channel><item><title>
  first_item_title = root.find(".//channel/item/title")
  
  if first_item_title:
    correct_answer = first_item_title.text.strip()
  else:
    print("没有找到博文标题")

  return question, correct_answer
