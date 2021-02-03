import scrapy
from .naver_articles import *
from scrapy.http import TextResponse
from get_url.items import GetUrlItem

class GetUrlSpider(scrapy.Spider):
    name = 'get_url'
    allow_domain=["https://news.naver.com"]
    
    user_agent= 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36'
    def start_requests(self):
        dates = get_day_list('2019/01/01', '2020/11/29')
        categ_s = [101, 102, 103, 105]
        #dates = list(divide_list(dates, 60))
        for date in dates:
            for categ in categ_s:
                for page in range(1, 250, 10):
                # 마지막 페이지로 
                    url = 'https://news.naver.com/main/list.nhn?mode=LSD&mid=sec&listType=title&sid1={}&date={}&page={}'.format(categ, date, page)
                    yield scrapy.Request(url, callback=self.parse)
                    
    def parse(self, resp):
        item = GetUrlItem()
        try:
            chk_next = resp.xpath('//div[@class="paging"]/a[@class="next nclicks(fls.page)"]/text()')[0].extract()
        except:
            chk_next = '끝'
        
        if chk_next == '끝':
            pages = resp.xpath('//a[@class="nclicks(fls.page)"]/text() | \
                //*[@id="main_content"]/div[@class="paging"]/strong/text()').extract()
            current_page = resp.url.split('page=')[1]
            if int(current_page) < int(pages[-1]):
                item['date'] = resp.url.split('date=')[1].split('&')[0]
                item['categ'] = resp.url.split('sid1=')[1].split('&')[0]
                item['last_p'] = pages[-1]

                yield item

            
            
