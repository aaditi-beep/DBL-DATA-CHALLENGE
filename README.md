# DBL Data Challenge — Airline Customer Service on Twitter

A data pipeline and analysis project studying how airlines handle customer
service interactions on Twitter: response times, sentiment, and conversation
flow, across multiple carriers.

## What this project does

- **Ingests** raw tweet/user data into MongoDB, cleaning malformed records and
  linking tweets into full conversation threads.
- **Engineers features** on top of the raw conversations: response time per
  reply, conversation flow labels, month/time tagging, language and location
  fields.
- **Runs sentiment analysis** on conversations two ways: a rule-based pass
  (VADER) for the main pipeline, and a transformer-based model
  (`cardiffnlp/twitter-xlm-roberta-base-sentiment`) benchmarked against the
  public TweetEval sentiment dataset, evaluated with a classification report
  and confusion matrix.
- **Aggregates analytics** per airline: average response time overall, per
  month, and per sentiment category.
- **Visualizes** results: response-time distributions, sentiment-evolution
  plots, per-airline comparisons, and colorblind-safe conversation-category
  breakdowns.

## Tech stack

Python, MongoDB (`pymongo`), pandas, VADER sentiment, HuggingFace
`transformers` (XLM-RoBERTa sentiment model) + `datasets` (TweetEval),
scikit-learn (classification report/confusion matrix), matplotlib/seaborn.

## Project map (by branch)

This was a team project built across feature branches during the challenge
sprint. The table below maps each stage of the pipeline to where the code
actually lives, so it's navigable without digging through branch history.

| Stage | Branch | What's there |
|---|---|---|
| Data cleaning & ingestion | `final_code_1_aaditi_macpro` | `clean_tweets_macpro_3`, `failed_clean_tweets_macpro`, `mongodb_clean_3b`, `mongodb_insertion_tweetsusers_macpro` |
| Conversation feature engineering | `delta_convos-10-11_June`, `months_to_tweets_collec_macpro` | response time, month tagging, place/language fields |
| Sentiment analysis (rule-based) | `final_code_1_aaditi_macpro` | `testing_sentiment_filter_tweets_6panes`, `convo_flow_etc_macpro` |
| Sentiment analysis (transformer, benchmarked) | `tweeteval_evaluation_plus_confusionmatrixcode` | `twitter_sentiment_eval_macpro.py` — evaluates XLM-RoBERTa sentiment on TweetEval, reports classification metrics + confusion matrix |
| Per-airline response-time analytics | `avg_response_time_per_airline_just_prints`, `per_airline_monthly_averages_and_DB_update` | average and monthly response time per airline |
| Visualizations | `plots_macpro` | histograms, KDE plots, heatmaps, per-airline bar charts, sentiment-evolution plots |
| Pipeline consolidation | `presentation_1_pipelines_Aaditi`, `final_code_1_aaditi_macpro` | end-to-end pipeline scripts used for the final presentation/demo |

`final_code_1_aaditi_macpro` is the most complete single branch — it contains
the consolidated cleaning → MongoDB → sentiment → response-time pipeline used
for the final demo.

## Setup

Requires a local or remote MongoDB instance. Scripts expect a database
matching the naming used in `mongodb_insertion_tweetsusers_macpro`
(`final_db_macpro_3`) — update the connection string/DB name at the top of
each script if yours differs.

```bash
pip install pymongo pandas matplotlib seaborn vaderSentiment transformers datasets scikit-learn torch
```

## Contributors

Built as part of TU/e's DBL Data Challenge. Aaditi Malhan led the MongoDB
pipeline, data cleaning, sentiment analysis (both VADER and the
transformer-based evaluation), response-time analytics, and the majority of
the visualizations.
