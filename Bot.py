from transformers import pipeline
from tweepy import OAuthHandler, Cursor, API
import os
from random import choice, randint
import time
import logging
import pandas as pd

logger = logging.getLogger()


class Twitter_Bot:
    def __init__(self, name, core, since_id):
        self.bot_name = name
        self.bot_core_values = core
        self.bot_since_id = since_id
    
    def twitterLogOn(self, ACCESS_TOKEN,ACCESS_TOKEN_SECRET,CONSUMER_KEY,CONSUMER_SECRET):
        auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
        auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
        api = API(auth, wait_on_rate_limit=True)

        try:
            api.verify_credentials()
        except Exception as e:
            logger.error("Error creating API", exc_info=True)
            raise e
        logger.info("API created")
        return api

    #get trending data in the United States from twitter
    def get_trending(api):
        trends = api.trends_place(id=23424977)
        trending = []
        for trend in trends[0]["trends"]:
            trending.append(trend["name"])
        return trending

    #get top 100 topics from twitter
    def get_topic_tweet(api, topic, max_tweets=100):
        searched_tweets = [
            status
            for status in Cursor(
                api.search, q=topic + " -filter:retweets", lang="en", tweet_mode="extended"
            ).items(max_tweets)
        ]
        found_tweets = []
        for tweet in searched_tweets:
            try:
                found_tweets.append(tweet.full_text)
            except:
                pass
        return found_tweets

    #https://realpython.com/twitter-bot-python-tweepy/
    def follow_followers(api):
        logging.basicConfig(level=logging.INFO)
        logger.info("Retrieving and following followers")
        for follower in Cursor(api.followers).items():
            if not follower.following:
                logger.info(f"Following {follower.name}")
                follower.follow()

    #https://realpython.com/twitter-bot-python-tweepy/
    def check_mentions(self, api, keywords, since_id):
        #main function needs:
        #since_id = 1
        #while True:
            #since_id = check_mentions(api, ["help", "support"], since_id)

        logging.basicConfig(level=logging.INFO)
        logger.info("Retrieving mentions")
        new_since_id = self.bot_since_id

        for tweet in Cursor(api.mentions_timeline,
            since_id=self.bot_since_id).items():
            new_since_id = max(tweet.id, new_since_id)
            if tweet.in_reply_to_status_id is not None:
                continue
            if any(keyword in tweet.text.lower() for keyword in keywords):
                logger.info(f"Answering to {tweet.user.name}")

                if not tweet.user.following:
                    tweet.user.follow()

                api.update_status(
                    status="Please reach out via DM",
                    in_reply_to_status_id=tweet.id,
                )
        return new_since_id

    #https://datascienceparichay.com/article/get-data-from-twitter-api-in-python-step-by-step-guide/
    #search_query = "#covid19 -filter:retweets", since="2020-09-16"
    def get_tweets(self, api, search_query, date_since, tweet_count):
        # get tweets from the API
        tweets = api.search_tweets(q=search_query, count=tweet_count,lang="en")#Cursor(api.search_tweets,q=search_query, lang="en",since=date_since).items(tweet_count)
        # intialize the dataframe
        tweets_df = pd.DataFrame()

        # store the API responses in a list
 
        for tweet in tweets:
            hashtags = []
    
            #print(tweet)
            try:
                for hashtag in tweet.entities["hashtags"]:
                    hashtags.append(hashtag["text"])
                text = api.get_status(id=tweet.id, tweet_mode='extended').full_text
                text = text.encode("ascii", "ignore").decode()

            except:
                pass
            finally:
                tweets_df = tweets_df.append(pd.DataFrame({'user_name': tweet.user.name, 
                                                'user_location': tweet.user.location,\
                                                'user_description': tweet.user.description,
                                                'user_verified': tweet.user.verified,
                                                'date': tweet.created_at,
                                                'text': text, 
                                                'hashtags': [hashtags if hashtags else None],
                                                'source': tweet.source}))
                tweets_df = tweets_df.reset_index(drop=True)
            
        return tweets_df






sleep_array = [10,15,20,25,30,35,40,45,50,55,60,65,70]

print('Loading Generator')
#EleutherAI/gpt-neo-125M
#EleutherAI/gpt-neo-1.3B
#EleutherAI/gpt-neo-2.7B
#generator = pipeline('text-generation', model='EleutherAI/gpt-neo-125M')





def generate_post(criteria, topic, max_length=None):
    import tokenizers
    print("Generating post on topic: " + topic)
    text = criteria + topic
    post = generator(text, max_length=max_length, do_sample=True, temperature=0.9,**encoded_input, pad_token_id=tokenizer.eos_token_id)[0]['generated_text']
    return post

def pick_a_topic(m):
    return randint(1,m)

def run_bot():
    #T_Bot = Twitter_Bot('Dave', ['','','',''], 'transportation')
    #api = T_Bot.twitterLogOn()
    while True:
        index = pick_a_topic(3)

        if index == 1:
            #trending = T_Bot.get_trending()
            #topic = choice(trending)
            post = generate_post('', 'What is beyond this life?',250)
        elif index == 2:
            post = generate_post('',"dad joke",250)
        elif index == 3:
            post = generate_post('',"something nice about mom",250)


        print("I am tweeting: " + post)
        #api.update_status(tweet)

        sleep = choice(sleep_array)
        print('Waiting ' + str(sleep) + ' minutes.')
        time.sleep(sleep*60)
   
T_Bot = Twitter_Bot('David', ['spiritual', 'shaman', 'yoga', 'mindfulness'], 1)
api = T_Bot.twitterLogOn(
    ACCESS_TOKEN = '1549572554997653504-58niqDXQthF8qRdBkIQn9MDpRqQHXb'
    ,ACCESS_TOKEN_SECRET = 'GL5ec1liwjAuwJFZCpUhO8XKmU371Q5EGWPpdYrVSS77d'
    ,CONSUMER_KEY = 'lDlPWJItFyiLaqGEGpV00z3F9'
    ,CONSUMER_SECRET = 'YQkTTTNMTGZJs5JAR5J7zDvyCHS8k90KCBi0U0veVmJMm1x5dp'
)

#https://developer.twitter.com/en/docs/twitter-api/tweets/search/integrate/build-a-query
query = '(' + " OR ".join(T_Bot.bot_core_values) + ') (-has:links AND -is:retweet AND -is:reply AND -is:nullcast AND -has:mentions)'
print(query)
#"#spiritual -filter:retweets"

df = T_Bot.get_tweets(api, query , '2022-07-01', 100)
print('printing df')
print(df)
df.to_csv('/Users\etromp\Desktop\Bot\\test.csv')



#if __name__ == "__main__":
    #run_bot()
