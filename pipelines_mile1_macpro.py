from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client['final_db_macpro_3']
tweets_collection = db['tweets_final_macpro_3']
users_collection = db['users_final_macpro_3']


#number of non-reply tweets (tweets that didn't reply to a different tweet)
num_non_reply_tweets = tweets_collection.count_documents( { 'in_reply_to_status_id_str': 'None' } )
print(f"There are {num_non_reply_tweets} non-reply tweets.")


#number of tweets, filtered by language
num_lang_tweets = tweets_collection.aggregate([
    { '$group': { '_id': '$lang', 'count': { '$sum': 1 } } }
])

print("Number of tweets per language:")
for lang in num_lang_tweets:
    print(f"Language: {lang['_id']}, Count: {lang['count']}")


#number of total language used in tweets
num_languages = len(tweets_collection.distinct('lang'))
print(f"Number of unique languages: {num_languages}")


#number of root tweets
num_root_tweets = tweets_collection.count_documents({ 'root': True })
print(f"There are {num_root_tweets} root tweets.")


#number of root tweets that don't have a reply
pipeline = [
    { '$match': { 'root': True } },
    {
        '$lookup': {
            'from': 'tweets_final_macpro_3',
            'localField': 'id_str',
            'foreignField': 'in_reply_to_status_id_str',
            'as': 'replies'
        }
    },
    { '$match': { 'replies': { '$size': 0 } } },
    { '$count': 'num_root_without_replies' }
]

result = list(tweets_collection.aggregate(pipeline))
count = result[0]['num_root_without_replies'] if result else 0

print(f"Number of root tweets without replies: {count}")


#number of reply tweets
num_reply_tweets = tweets_collection.count_documents({"in_reply_to_status_id_str": { "$ne": "None" } })
print(f"There are {num_reply_tweets} reply tweets.")


#number of verified and non-verified users
user_counts = users_collection.aggregate([
    {
        '$group': {
            '_id': '$verified',
            'count': { '$sum': 1 }
        }
    }
])

print("Verified vs. Non-Verified User Counts:")
for result in user_counts:
    status = "Verified" if result['_id'] else "Non-Verified"
    print(f"{status}: {result['count']}")











