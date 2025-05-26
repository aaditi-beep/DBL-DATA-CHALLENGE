from pymongo import MongoClient
import time

client = MongoClient("mongodb://localhost:27017")
db = client['final_db']   # Your test DB here
tweets_collection = db['tweets']
users_collection = db['users']
conversations_collection = db['conversations']


#for tweet in tweets_collection.find():
#    print(f'{tweet['in_reply_to__id_str']},\t {type(tweet['in_reply_to_status_id_str'])}\n\n')
    


# Airline user IDs as strings
airline_ids = {
    "18332190", "56377143", "38676903", "218730857", "1542862735",
    "22536055", "20626359", "253340062", "124476322", "45621423",
    "260907612", "5920532", "13192972", "21964954", "21764143",
    "6449282", "334032462", "821045162", "17077093", "387573617",
    "16629918", "7212562"
}



def unwrap_long(value):
    # If value is dict with $numberLong, return as int; else return as is
    if isinstance(value, dict) and "$numberLong" in value:
        return int(value["$numberLong"])
    return value

def find_root_tweet(tweet, participants):
    reply_id = tweet['in_reply_to_status_id_str']
    if reply_id == 'None':
        return (tweet['_id'], participants)
    parent = tweets_collection.find_one({'id_str': reply_id})
    if parent:
        # Add parent's tweet id to participants (tweet ids are int)
        return find_root_tweet(parent,  [parent['_id']] + participants)
    return (tweet['_id'], participants)

def same_convo(chain_1, chain_2):
    min_len = min(len(chain_1), len(chain_2))
    for i in range(min_len):
        if chain_1[i] != chain_2[i]:
            return 3
    if len(chain_2) == len(chain_1) + 1:
        return 1
    elif len(chain_2) > len(chain_1) + 1 and chain_2[:len(chain_1)] == chain_1:
        return 2
    elif len(chain_2) < len(chain_1) and chain_1[:len(chain_2)] == chain_2:
        return 4
    return 0

start_time = time.time()

# Clear old conversations collection first
conversations_collection.delete_many({})

# Create conversations for root tweets
ci = 1
for root in tweets_collection.find({'root': True}):
    user_id = root['user_id_str']
    conversation = {
        '_id': f'c{ci}',
        'root_tweet': root['_id'],
        'tweets': [root['_id']],
        'participants': [user_id],
        'airline': user_id if user_id in airline_ids else None
    }
    conversations_collection.insert_one(conversation)
    tweets_collection.update_one({'_id': root['_id']}, {'$addToSet': {'conversation_ids': conversation['_id']}})
    ci += 1

# Process replies
for tweet in tweets_collection.find({'root': False}):
    root_id, participants_chain = find_root_tweet(tweet, [tweet['_id']])
    root_tweet = tweets_collection.find_one({'_id': root_id, 'root': True})
    
    print(f'{root_id}, {participants_chain}')
    
    
    if not root_tweet:
        continue

    # Mark root tweet as replied
    tweets_collection.update_one({'_id': root_id}, {'$set': {'replied': True}})

    root_convos = list(conversations_collection.find({'root_tweet': root_id}))
    # Convert tweet IDs chain to user_id_str list for participants
    participants_users = []
    for tid in participants_chain:
        t = tweets_collection.find_one({'_id': tid})
        if t:
            uid = t['user_id_str']
            if uid not in participants_users:
                participants_users.append(uid)

    for convo in root_convos:
        conv_tweets = convo['tweets']
        ctype = same_convo(conv_tweets, participants_chain)
        if ctype == 3:
            continue
        if ctype == 1:
            # Add last tweet and user to convo
            last_tid = participants_chain[-1]
            last_tweet = tweets_collection.find_one({'_id': last_tid})
            if last_tweet:
                conversations_collection.update_one(
                    {'_id': convo['_id']},
                    {
                        '$addToSet': {
                            'tweets': last_tid,
                            'participants': last_tweet['user_id_str'],
                        }
                    }
                )
            break
        elif ctype == 2:
            # Add all new tweets and users from participants_chain
            for tid in participants_chain[len(conv_tweets):]:
                t = tweets_collection.find_one({'_id': tid})
                if t:
                    conversations_collection.update_one(
                        {'_id': convo['_id']},
                        {
                            '$addToSet': {
                                'tweets': tid,
                                'participants': t['user_id_str'],
                            }
                        }
                    )
            break
        else:
            break
    else:
        # No matching conversation found, create new convo
        new_id = f'c{ci}'
        convo_participants = [root_tweet['user_id_str']] + participants_users
        conversation = {
            '_id': new_id,
            'root_tweet': root_id,
            'tweets': [root_id] + participants_chain,
            'participants': list(dict.fromkeys(convo_participants)),  # remove duplicates preserving order
            'airline': root_tweet['user_id_str'] if root_tweet['user_id_str'] in airline_ids else None
        }
        conversations_collection.insert_one(conversation)
        tweets_collection.update_one({'_id': root_id}, {'$addToSet': {'conversation_ids': new_id}})
        ci += 1
        

# Delete conversations with less than 2 participants
constraint1 = conversations_collection.delete_many({
    '$expr': {'$lt': [{'$size': "$participants"}, 2]}
})

# Delete conversations with less than 3 tweets
constraint2 = conversations_collection.delete_many({
    '$expr': {'$lt': [{'$size': "$tweets"}, 3]}
})

# Delete conversations where none of the participants are airlines
constraint3 = conversations_collection.delete_many({
    'participants': {'$not': {'$elemMatch': {'$in': list(airline_ids)}}}
})




end_time = time.time()
print(f"Reconstruction done in {end_time - start_time:.2f} seconds")

