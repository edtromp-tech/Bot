from transformers import pipeline
import twitter_credentials as tc
from tweepy import OAuthHandler, Cursor, API
import os
from random import choice, random
import time

sleep_array = [10,15,20,25,30,35,40,45,50,55,60,65,70]
print('Loading Generator')
generator = pipeline('text-generation', model='EleutherAI/gpt-neo-1.3B')#change to 2.7B but will cost 10GB

ACCESS_TOKEN = "your creds"
ACCESS_TOKEN_SECRET = "your creds"
CONSUMER_KEY = "your creds"
CONSUMER_SECRET = "your creds"


def twitterLogOn():
    auth = OAuthHandler(tc.CONSUMER_KEY, tc.CONSUMER_SECRET)
    auth.set_access_token(tc.ACCESS_TOKEN, tc.ACCESS_TOKEN_SECRET)
    api = API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)
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

def generate_tweet(topic):
    print("Generating tweet on topic: " + topic)
    text = 'Create a tweet that is less than 280 characters long based on ' + topic
    tweet = generator(text, max_length=280, do_sample=True, temperature=0.9)[0]['generated_text']

    if len(tweet) > 280:
        tweet = tweet[:280]
    return tweet

def pick_a_topic(m):
    return random.randint(1,m)

def run_bot():
    api = twitterLogOn()
    while True:
        index = pick_a_topic(3)

        if index == 1:
            trending = get_trending()
            topic = choice(trending)
            tweet = generate_tweet(topic)
        elif index == 2:
            tweet = generate_tweet("dad joke")
        elif index == 3:
            tweet = generate_tweet("something nice about mom")

        print("I am tweeting: " + tweet)
        api.update_status(tweet)

        sleep = choice(sleep_array)
        time.sleep(sleep*60)


if __name__ == "__main__":
    run_bot()
