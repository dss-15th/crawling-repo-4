import time
import re
import requests
import scrapy
from .get_url_check_last_page import get_urls
from scrapy.http import TextResponse
from scrapy_naver_news_everyday.items import ScrapyNaverNewsEverydayItem

class ScrapyNaverNewsEverydaySpider(scrapy.Spider):
    name = 'scrapy_naver_news_everyday'
    allow_domain=["https://news.naver.com"]
    categ = {#'정치': '100',
     '101':'경제',
     '102': '사회',
     '103': '생활/문화',
     #'세계': '104',
     '105': 'IT/과학'}
    user_agent= 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
    def start_requests(self):
        all_category_urls = []
        for category in self.categ.keys():
            all_category_urls.append(get_urls(category))

        for urls in all_category_urls:
            for url in urls:
                yield scrapy.Request(url, callback=self.parse)
            time.sleep(10)
            
    def parse(self, resp):
        links = resp.xpath('//*[@id="main_content"]/div[2]/ul/li/a/@href').extract()
        # links = [resp.urljoin(link) for link in links]
        for link in links:
            yield scrapy.Request(link, callback=self.parse_content)
            
    def parse_content(self, resp):
        item = ScrapyNaverNewsEverydayItem()
        title = resp.xpath('//*[@id="articleTitle"]/text() | //*[@id="content"]/div[1]/div/h2/text()')[0].extract()
        date = resp.xpath('//*[@id="main_content"]/div[1]/div[3]/div/span[@class="t11"]/text() | \
                        //div[@class="article_info"]/span[@class="author"]/em')[0].extract()
        content = resp.xpath('//*[@id="articleBodyContents"]/text() | \
                        //*[@id="articleBodyContents"]/strong/text() | \
                        //*[@id="articleBodyContents"]/div/text() | \
                        //*[@id="articleBodyContents"]/div/div/text() | \
                        //*[@id="articleBodyContents"]/font/text() | \
                        //*[@id="articleBodyContents"]/div[2]/ul/li/span/span/text() | \
                        //*[@id="articeBody"]/text()').extract()
        content = [text.replace('\xa0', ' ').strip() for text in content]
        try:
            c_num = resp.url.split('sid1=')[1].split('&')[0]
        
            item['date'] = re.findall('[0-9]{4}[.][0-9]{2}[.][0-9]{2}', date)[0]
            item['category'] = self.categ[c_num]
            item['press_agency'] = resp.xpath('//a[@class="nclicks(atp_press)"]/img/@title | //div[@class="press_logo"]/a/img/@alt')[0].extract()
            item['link'] = resp.url
            item['title'] = title.strip()
            item['content'] = '\n'.join(content).strip()

            yield item
        except:
            print('nope') # url에 카테고리가 없는 연예기사 스포츠기사는 제외