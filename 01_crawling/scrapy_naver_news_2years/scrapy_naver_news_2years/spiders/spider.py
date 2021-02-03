import pandas as pd
import time
import re
import requests
import scrapy
from scrapy.http import TextResponse
from scrapy_naver_news_2years.items import ScrapyNaverNews2YearsItem

class ScrapyNaverNews2YearsSpider(scrapy.Spider):
    name = 'scrapy_naver_news_2years'
    allow_domain=["https://news.naver.com"]
    user_agent= 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
    categ = {#'정치': '100',
    '101':'economy',
    '102': 'soci',
    '103': 'culture',
    #'세계': '104',
    '105': 'IT'}

    def __init__(self, categ = 101, *args, **kwargs): 
        self.categ_path = self.categ[str(categ)] + '.csv'
        print(self.categ_path)
        ScrapyNaverNews2YearsSpider.__init__(self)

    def start_requests(self):
        #df = pd.read_csv('article_url_1.csv')
        df = pd.read_csv(self.categ_path)
        rows = df.iloc
        date_ex = '202011'
        
        for row in rows:
            date_ = str(row['date'])
            date_ = str(date_)[0:7]
            if date_ != date_ex:
                time.sleep(2)
            #print(row['categ'], row['date'], row['last_p'])
            for page in range(1, int(row['last_p'])+1):
                url = 'https://news.naver.com/main/list.nhn?mode=LSD&mid=sec&listType=title&sid1={}&date={}&page={}'.format(row['categ'], row['date'], page)
                yield scrapy.Request(url, callback=self.parse)
            date_ex = str(date_)[0:7]
            
    def parse(self, resp):
        links = resp.xpath('//*[@id="main_content"]/div[2]/ul/li/a/@href').extract()
        
        # links = [resp.urljoin(link) for link in links]
        for link in links:
            yield scrapy.Request(link, callback=self.parse_content)
            
    def parse_content(self, resp):
        item = ScrapyNaverNews2YearsItem()
        title = resp.xpath('//*[@id="articleTitle"]/text() | //*[@id="content"]/div[1]/div/h2/text() | \
            //h4[@class="title"]/text()')[0].extract()
        date = resp.xpath('//*[@id="main_content"]/div[1]/div[3]/div/span[@class="t11"]/text() | \
                        //div[@class="article_info"]/span[@class="author"]/em/text()|\
                        //div[@class="info"]/span[1]/text()')[0].extract()
        content = resp.xpath('//*[@id="articleBodyContents"]/text() | \
                        //*[@id="articleBodyContents"]/strong/text() | \
                        //*[@id="articleBodyContents"]/div/text() | \
                        //*[@id="articleBodyContents"]/div/div/text() | \
                        //*[@id="articleBodyContents"]/font/text() | \
                        //*[@id="articleBodyContents"]/div[2]/ul/li/span/span/text() | \
                        //*[@id="newsEndContents"]/text() | \
                        //*[@id="articeBody"]/text()').extract()
        content = [text.replace('\xa0', ' ').strip() for text in content]
        categ_num = resp.url.split('sid1=')[1].split('&')[0]
        
        item['date'] = re.findall('[0-9]{4}[.][0-9]{2}[.][0-9]{2}', date)[0]
        item['category'] = self.categ[categ_num]
        item['press_agency'] = resp.xpath('//a[@class="nclicks(atp_press)"]/img/@title | //div[@class="press_logo"]/a/img/@alt | \
                                          //*[@id="pressLogo"]/a/img/@alt')[0].extract()
        item['link'] = resp.url
        item['title'] = title.strip()
        item['content'] = '\n'.join(content).strip()
        
        yield item