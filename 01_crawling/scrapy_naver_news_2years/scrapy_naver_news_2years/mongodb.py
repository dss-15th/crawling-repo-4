import pymongo
# DB와 연결
client = pymongo.MongoClient('mongodb://127.0.0.1:27017/') 
# DB Table 지정
db = client.news
collection = db.articles_society