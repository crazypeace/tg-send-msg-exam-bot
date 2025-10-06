import requests
from bs4 import BeautifulSoup

def buildQA():
  question = '我的博客的最新一期博文标题是什么?'
  correct_answer = ''

  url = "https://zelikk.blogspot.com/"

  # 请求网页
  response = requests.get(url)

  # 解析 HTML
  soup = BeautifulSoup(response.text, "html.parser")

  # 找到第一个 class="post-title entry-title" 的元素
  element = soup.find(class_="post-title entry-title")

  if element:
    correct_answer = element.get_text(strip=True)
  else:
    print("没有找到目标元素")

  return question, correct_answer