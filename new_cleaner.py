import pandas as pd
import json
import os
from glob import glob

# Input folder containing all .json files
input_folder = r"E:\data"
json_files = glob(os.path.join(input_folder, "*.json"))

# Output folder structure
json_output_folder = r"C:\Users\styli\Desktop\temp\coding_london\out_new"

# Ensure output folder exists
os.makedirs(json_output_folder, exist_ok=True)

# Column lists
vars_2b_scrapped_main_df = [
    "display_text_range", "in_reply_to_status_id", "geo", "source", "coordinates", "is_quote_status",
    "quote_count", "reply_count", "retweet_count", "favorite_count", "id", "contributors",
    "truncated", "extended_tweet", "favorited", "retweeted", "filter_level", "user", "entities",
    "retweeted_status", "quoted_status"
]

vars_2b_scrapped_user_df = [
    "description", "name", "location", "url", "translator_type", "protected", "friends_count",
    "listed_count", "favourites_count", "created_at", "utc_offset", "time_zone", "geo_enabled",
    "is_translator", "lang", "contributors_enabled", "id", "following", "follow_request_sent", "notifications",
    "profile_background_color", "profile_background_tile", "profile_link_color", "profile_sidebar_border_color",
    "profile_text_color", "profile_use_background_image", "profile_image_url", "profile_image_url_https",
    "profile_banner_url", "default_profile", "default_profile_image"
]

def safe_json_loads(json_str):
    if pd.isna(json_str):
        return None
    try:
        return json.loads(str(json_str))
    except (json.JSONDecodeError, TypeError):
        return None

def var_cleaner(dataframe, vars_2b_scrapped: list) -> bool:
    try:
        for key in vars_2b_scrapped:
            if key in dataframe.columns:
                del dataframe[key]
            else:
                print(f"The column '{key}' is missing in the DataFrame.")
    except Exception as err:
        print(f"\n\nVariable cleaner FAILED")
        print(f"Unexpected {err=}, {type(err)=}")

def grab_id_str(entities) -> str:
    try:
        return entities[0]['id_str']
    except (TypeError, KeyError, IndexError):
        return ""

def grab_hashtag_text(entities) -> str:
    try:
        return entities[0]['text']
    except (TypeError, KeyError, IndexError):
        return ""

if __name__ == '__main__':
    for idx, input_file in enumerate(json_files):
        try:
            print(f"\nProcessing file {idx + 1}/{len(json_files)}: {input_file}")

            # Specify the data type for string-based IDs when reading the JSON
            dtype = {
                'id_str': str,
                'in_reply_to_user_id': str,
                'in_reply_to_user_id_str': str,
                'user.id_str': str,  # Handle user ID string directly
                'in_reply_to_status_id_str': str
            }
            df_all = pd.read_json(input_file, lines=True, dtype=dtype)

            # Extract hashtags
            df_entities = pd.json_normalize(df_all['entities'])
            df_all['entities_hashtags'] = df_entities['hashtags'].apply(grab_hashtag_text)

            # Extract user mentions
            df_all['entities_user_mentions'] = df_entities['user_mentions'].apply(grab_id_str)

            # Overwrite truncated tweets with full_text from extended_tweet
            mask = df_all['truncated'] == True
            df_all.loc[mask, 'text'] = df_all.loc[mask, 'extended_tweet'].apply(
                lambda d: d.get('full_text', '') if isinstance(d, dict) else ''
            )

            # Create user DataFrame and join
            df_user = pd.json_normalize(df_all['user'])
            var_cleaner(df_user, vars_2b_scrapped_user_df)
            df_user.rename(columns=lambda x: 'user_' + x, inplace=True)
            df_all = df_all.join(df_user)

            # Clean main df
            var_cleaner(df_all, vars_2b_scrapped_main_df)

            # Output file name
            base_filename = os.path.splitext(os.path.basename(input_file))[0]
            json_out_path = os.path.join(json_output_folder, f"{base_filename}_output.json")

            # Export only cleaned df_all to JSON
            df_all.to_json(json_out_path, orient='records', lines=True, force_ascii=False)

        except Exception as err:
            print(f"Error processing {input_file}: {err}")
