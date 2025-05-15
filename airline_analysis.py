from pymongo import MongoClient
from collections import defaultdict
import pandas as pd
from datetime import datetime

# MongoDB connection
client = MongoClient("mongodb://localhost:27017")
db = client["your_database_name"]
tweets = db["your_collection_name"]



# List of airlines you care about
airlines = [
    "KLM", "AirFrance", "British_Airways", "AmericanAir", "Lufthansa", "AirBerlin",
    "AirBerlin assist", "easyJet", "RyanAir", "SingaporeAir", "Qantas",
    "EtihadAirways", "VirginAtlantic"
]

pipeline_tweet_counts = [
    {"$match": {"airline": {"$in": airlines}}},
    {"$group": {"_id": "$airline", "tweet_count": {"$sum": 1}}}
]

tweet_counts = list(tweets.aggregate(pipeline_tweet_counts))
print("Tweet counts per airline:", tweet_counts)

pipeline_avg_convo_len = [
    {"$match": {"airline": {"$in": airlines}}},
    {"$group": {
        "_id": {"airline": "$airline", "conversation_id": "$conversation_id"},
        "convo_size": {"$sum": 1}
    }},
    {"$group": {
        "_id": "$_id.airline",
        "avg_convo_length": {"$avg": "$convo_size"}
    }}
]

avg_convo_lengths = list(tweets.aggregate(pipeline_avg_convo_len))
print("Average conversation lengths per airline:", avg_convo_lengths)

pipeline_convos_per_month = [
    {"$match": {"airline": {"$in": airlines}}},
    {"$group": {
        "_id": {
            "airline": "$airline",
            "conversation_id": "$conversation_id",
            "year_month": {
                "$dateToString": {"format": "%Y-%m", "date": "$created_at"}
            }
        }
    }},
    {"$group": {
        "_id": {
            "airline": "$_id.airline",
            "year_month": "$_id.year_month"
        },
        "num_convos": {"$sum": 1}
    }},
    {"$sort": {"_id.year_month": 1}}
]

convos_per_month = list(tweets.aggregate(pipeline_convos_per_month))
df = pd.DataFrame(convos_per_month)
df["_id"] = df["_id"].apply(lambda x: (x["airline"], x["year_month"]))
df.columns = ["(Airline, Month)", "Conversation Count"]
print(df)
