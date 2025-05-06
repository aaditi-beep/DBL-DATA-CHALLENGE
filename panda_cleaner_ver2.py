import pandas as pd
import json
import os


input_file  = r"E:\data\airlines-1558527599826.json"

vars_2b_scrapped_main_df = [
    "display_text_range", "in_reply_to_status_id", "geo", "source", "coordinates", "is_quote_status",
    "quote_count", "reply_count", "retweet_count", "favorite_count", "id", "contributors", # "url" probably doesn't exist
    "truncated", "extended_tweet", "favorited", "retweeted", "filter_level", "user", "entities"
    , "retweeted_status", "quoted_status"
]


vars_2b_scrapped_user_df = [
    "description", "name", "location", "url", "translator_type", "protected", "friends_count",
    "listed_count", "favourites_count", "created_at", "utc_offset", "time_zone", "geo_enabled",
    "is_translator", "lang", "contributors_enabled", "id", "following", "follow_request_sent", "notifications",
    "profile_background_color", "profile_background_image_url", "profile_background_image_url_https",
    "profile_background_tile", "profile_link_color", "profile_sidebar_border_color", "profile_sidebar_fill_color",
    "profile_text_color", "profile_use_background_image", "profile_image_url", "profile_image_url_https",
    "profile_banner_url", "default_profile", "default_profile_image"
]


## Global variables
df_all = None
df_user = None
df_extended_tweet = None


def safe_json_loads(json_str):
    if pd.isna(json_str):
        return None # Return None for missing values
    try:
        # Ensure it's treated as a string before parsing
        return json.loads(str(json_str))
    except (json.JSONDecodeError, TypeError):
        return None # Return None if parsing fails



def var_cleaner(dataframe, vars_2b_scrapped:list) -> bool:
    try:
        for key in vars_2b_scrapped:
            if key in dataframe.columns:
                del dataframe[key]
            else:
                print(f"The column '{key}' is missing in the DataFrame.")
        

            
    except Exception as err:
        print(f"\n\nVariable cleaner FAILED")
        print(f"Unexpected {err=}, {type(err)=}")
        

## Extracts IDs from the user_mentions dict

def grab_id_str(entities) -> str:
    try:
        return entities[0]['id_str']
    except:
        return ""
    
def grab_hashtag_text(entities) -> str:
    try:
        return entities[0]['text']
    except:
        return ""
    
    

    


if __name__ == '__main__':
    try:
        df_all = pd.read_json(input_file, lines = True)
    except Exception as err:
        print(f"Failed reading json file {err=}, {type(err)=}")
        
    
    
    
    ## hashtags extraction
    df_entities = pd.json_normalize(df_all['entities'])
    df_all['entities_hashtags'] = df_entities['hashtags'].apply(grab_hashtag_text)
    
    ## user mentions extraction
    df_all['entities_user_mentions'] = df_entities['user_mentions'].apply(grab_id_str)
    
    
    ## extended tweet dataframe creation (before it gets purged)
    extended_tweet_list = df_all['extended_tweet'].tolist()
    df_extended_tweet = pd.DataFrame([extended_tweet if isinstance(extended_tweet, dict) else {} for extended_tweet in extended_tweet_list], index=df_all.index)
    df_extended_tweet.to_excel("lala_extended_tweet.xlsx")
    
    ## boolean mask to find ones to be truncated
    mask = df_all['truncated'] == True

    # overwrite only those rows’ text with the full_text from extended_tweet
    df_all.loc[mask, 'text'] = df_all.loc[mask, 'extended_tweet'].apply(lambda d: d.get('full_text', ''))
        
    
    
    
    ## create user dataframe
    
    df_user = pd.json_normalize(df_all['user'])
    
    df_user.to_excel("lala_user.xlsx")
    var_cleaner(df_user, vars_2b_scrapped_user_df)
    ## renames columns for clarity
    df_user.rename(columns=lambda x: 'user_' + x, inplace=True)
    df_user.to_excel("lala_cleaned_user.xlsx")
    

  
    # cleanup main dataframe    
    var_cleaner(df_all, vars_2b_scrapped_main_df)
    #print(df_all)
    
    ## joins the user dataframe to the df_all main
    df_all = df_all.join(df_user)
    
    df_all['created_at'] = df_all['created_at'].dt.tz_localize(None)
    df_all['timestamp_ms'] = df_all['timestamp_ms'].dt.tz_localize(None)   
    df_all.to_excel("lala_cleaned.xlsx")
    
    ## exports it to json form
    temp_out = r'C:\Users\styli\Desktop\temp\coding_london\out\output.json'
    df_all.to_json(temp_out, orient='records', lines=True)

    

    

    
    
