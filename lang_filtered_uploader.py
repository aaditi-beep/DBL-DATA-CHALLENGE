from pymongo import MongoClient
import json
import os
import datetime
from decimal import Decimal, getcontext

client = MongoClient("mongodb://localhost:27017")
db = client['final_db']
tweets_collection = db['tweets']
users_collection = db['users']

# Global variables
users_mongo = set()
directory = r'C:\Users\styli\Desktop\temp\coding_london\out_new'

allowed_langs = {'en', 'es', 'fr', 'nl'}

ti = 1

for file in os.listdir(directory):  # loops through all json files
    path = os.path.join(directory, file)

    with open(path, 'r', encoding='utf-8') as f:  # open each json file
        for line in f:  # loop through each tweet object
            tweet_obj = json.loads(line)  # creates a json object

            try:
                if tweet_obj['delete']:
                    continue
            except KeyError:
                pass
            
            '''
            getcontext().prec = 50
            
            try:
                print(f'{tweet_obj['in_reply_to_status_id_str']}, {Decimal(tweet_obj['in_reply_to_status_id_str'])}')
            except Exception as e:
                print(f'{e}')
            '''
            
            # Convert 'created_at' timestamp from ms to formatted string (once)
            timestamp_ms = tweet_obj.get('created_at')
            if timestamp_ms:
                try:
                    dt = datetime.datetime.fromtimestamp(timestamp_ms / 1000, tz=datetime.timezone.utc)
                    tweet_obj['created_at'] = dt.strftime('%Y-%m-%d %H:%M:%S')
                except Exception as e:
                    print(f"Error converting created_at for tweet {tweet_obj.get('id_str')}: {e}")

            # --- Language Filter Block --- #
            tweet_lang = tweet_obj.get('lang')
            if tweet_lang not in allowed_langs:
                continue  # Skip this tweet if language is not allowed

            tweet_id = tweet_obj['id_str']  # keep as string for Mongo _id consistency
            user_id = tweet_obj['user_id_str']

            if user_id not in users_mongo:  # checks if user document was already created
                users_mongo.add(user_id)
                user = {
                    "_id": user_id,
                    "verified": tweet_obj.get('user_verified'),
                    "screen_name": tweet_obj.get('user_screen_name'),
                    "followers_count": tweet_obj.get('user_followers_count'),
                    "statuses_count": tweet_obj.get('user_statuses_count')
                }
                users_collection.insert_one(user)  # add to mongo user collection

            # Clean up tweet object by removing unwanted fields
            
            if tweet_obj['in_reply_to_status_id_str'] == 'None':  # checks if it's null
                tweet_obj['root'] = True
            else:
                tweet_obj['root'] = False

            try:
                tweet_obj['_id'] = ti
                tweets_collection.insert_one(tweet_obj)
                ti+=1
            except Exception as e:
                print(f'{tweet_obj["_id"]}, {e}')
                continue
                
