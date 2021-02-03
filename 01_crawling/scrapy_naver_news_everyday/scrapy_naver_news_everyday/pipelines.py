# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from .mongodb import collection
import time

class ScrapyNaverNewsEverydayPipeline:
    def process_item(self, item, spider):
        # time.sleep(10)
        data = {
            'p_date': item['date'],
            'category': item['category'],
            'press_agency': item['press_agency'],
            'link': item['link'],
            'title': item['title'],
            'content': item['content'],
            }
        print('='*5)
        collection.insert(data)
        return item