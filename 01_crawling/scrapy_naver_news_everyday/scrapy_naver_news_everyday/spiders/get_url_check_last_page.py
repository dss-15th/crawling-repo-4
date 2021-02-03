import requests
import scrapy
from scrapy.http import TextResponse
from datetime import datetime, timedelta

def get_urls(category='105'):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
    }
    date = (datetime.today() - timedelta(1)).strftime('%Y%m%d')
    last_p, urls = '', []
    for page in range(1, 1000, 10):
        # 마지막 페이지로 
        url = 'https://news.naver.com/main/list.nhn?mode=LSD&mid=sec&listType=title&sid1={}&date={}&page={}'.format(category, date, page)
        req = requests.get(url, headers=headers)
        resp = TextResponse(req.url, body=req.text, encoding='utf-8')

        try:
            chk_next = resp.xpath('//div[@class="paging"]/a[@class="next nclicks(fls.page)"]/text()')[0].extract()
        except:
            chk_next = '끝'

        if chk_next == '끝':
            # 마지막 페이지가 여러개일때
            # 마지막 페이지가 1개일때
            pages = resp.xpath('//a[@class="nclicks(fls.page)"]/text()' |
                              '//div[@class="paging"]/strong').extract() 
            last_p = pages[-1]
            print(last_p)
            break

    for page in range(1, int(last_p)+1):
        urls.append('https://news.naver.com/main/list.nhn?mode=LSD&mid=sec&listType=title&sid1={}&date={}&page={}'.format(category, date, page))
    return urls