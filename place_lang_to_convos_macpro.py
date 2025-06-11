from pymongo import MongoClient
from datetime import datetime

client = MongoClient("mongodb://localhost:27017")
db = client['final_db_macpro_3']   
tweets_collection = db['tweets_final_macpro_3']
conversations_collection = db['convos_final_macpro_4']

i = 0
for convo in conversations_collection.find():
    root_tweet_obj = tweets_collection.find_one({'_id': convo['root_tweet']})
    lan = root_tweet_obj['lang']
    if root_tweet_obj['place']:
        city = root_tweet_obj['place']['name']
        country = root_tweet_obj['place']['country']

        conversations_collection.update_one(
            {"_id": convo['_id']},
            {"$set": {
            "lang": lan, 
            "city": city if city else "undefined",
            "country": country if country else "undefined"
            }}
            )
    else:
        conversations_collection.update_one(
            {"_id": convo['_id']},
            {"$set": {
            "lang": lan, 
            "city": "undefined",
            "country": "undefined"
            }}
        )

    i += 1 
    if i % 10000 == 0:
        print(f'{i} conversations processed')

#remove the place field
from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client['final_db_macpro_3']
convos_collection = db['convos_final_macpro_4']

# Remove the 'place' field from all documents
result = convos_collection.update_many(
    {},
    {"$unset": {"place": ""}}
)

print(f"Matched {result.matched_count} docs, modified {result.modified_count} docs.")
