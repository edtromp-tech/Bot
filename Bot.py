#from transformers import pipeline
from tweepy import OAuthHandler, Cursor, API
import os
from random import choice, randint
import time
import logging
import pandas as pd
from random import randrange
logger = logging.getLogger()

BASE_DIR = 'C:\\Users\\etromp\\OneDrive - ZTRIP\\Bot\\'



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


    def post_tweets(self, api, tweet, image = None):
        # Upload image
        if image != None:
            media = api.media_upload(image)
            # Post tweet with image
            post_result = api.update_status(status=tweet, media_ids=[media.media_id])
        else:
            post_result = api.update_status(status=tweet)
        print(post_result)

sleep_array = [10,15,20,25,30,35,40,45,50,55,60,65,70]

print('Loading Generator')
#EleutherAI/gpt-neo-125M
#EleutherAI/gpt-neo-1.3B
#EleutherAI/gpt-neo-2.7B
#generator = pipeline('text-generation', model='EleutherAI/gpt-neo-125M')

def getNews(query):
    print('Getting News...')
    import requests
    import pandas as pd
    from json import dumps, loads
    f = BASE_DIR + 'private.csv'

    df = pd.read_csv(f, header=None, index_col=False)
    df.columns = ['Name', 'Value']
    key = df.loc[df['Name'] == 'X-RapidAPI-Key', 'Value'].values[0]
    host = df.loc[df['Name'] == 'X-RapidAPI-Host', 'Value'].values[0]

    url = "https://contextualwebsearch-websearch-v1.p.rapidapi.com/api/Search/ImageSearchAPI"
    headers = {
        "X-RapidAPI-Key": key,
        "X-RapidAPI-Host": host
    }


    querystring = {"q": query, "pageNumber": "1", "pageSize": "5", "autoCorrect": "true"}
    response = requests.request("GET", url, headers=headers, params=querystring)

    res = loads(response.text)
    tmp = res['value']
    df = pd.read_json(dumps(tmp))

    loop_count = 0
    while True:
        if df.shape()[0] <=0:
            post = "I thought I had a good news article but I must have misplaced it.  \n#DaveTheBot #Automation #forgetfull"
            break
        image_url = df.iloc[loop_count]['url']
        web_url = df.iloc[loop_count]['webpageUrl']
        post = df.iloc[loop_count]['title']

        img_data = requests.get(image_url).content
        img_name = BASE_DIR + 'test_image.jpg'
        with open(img_name, 'wb') as handler:
            handler.write(img_data)
        img_name = BASE_DIR + 'test_image.jpg'

        post = "News Drop\n\n" + post + "\n" + web_url + "\n\n#DaveTheBot #automation #" + query
        if len(post) < 250:
            break

        if loop_count > 4:
            post = "I thought I had a good news article but I must have misplaced it. #forgetfull #DaveTheBot #automation"
            break
        loop_count += 1

    return post, img_name

def getImages(query):
    print('Getting images...')
    import requests
    import pandas as pd
    from json import dumps, loads
    f = BASE_DIR + 'private.csv'

    df = pd.read_csv(f, header=None, index_col=False)
    df.columns = ['Name', 'Value']
    key = df.loc[df['Name'] == 'X-RapidAPI-Key', 'Value'].values[0]
    host = df.loc[df['Name'] == 'X-RapidAPI-Host', 'Value'].values[0]

    url = "https://contextualwebsearch-websearch-v1.p.rapidapi.com/api/Search/ImageSearchAPI"

    querystring = {"q":query,"pageNumber":"1","pageSize":"5","autoCorrect":"true","safeSearch":"false"}

    headers = {
        "X-RapidAPI-Key": key,
        "X-RapidAPI-Host": host
    }
    response = requests.request("GET", url, headers=headers, params=querystring)

    res = loads(response.text)
    tmp = res['value']
    df = pd.read_json(dumps(tmp))
    image_url = df.iloc[randrange(5)]['url']

    img_data = requests.get(image_url).content
    img_name = BASE_DIR + 'test_image.jpg'
    with open(img_name, 'wb') as handler:
        handler.write(img_data)
    post = "#DaveTheBot #automation"
    return post, BASE_DIR + 'test_image.jpg'

def getQuote(query):
    print('Getting quotes...')
    import requests
    import pandas as pd
    from json import dumps, loads
    f = BASE_DIR + 'private.csv'

    df = pd.read_csv(f, header=None, index_col=False)
    df.columns = ['Name', 'Value']
    key = df.loc[df['Name'] == 'ZenQuotes-Key', 'Value'].values[0]

    url = "https://zenquotes.io/api/quotes/"+key
    #url = "https://zenquotes.io/api/random/"+key

    querystring = {"keyword": query}
    response = requests.request("GET", url, params=querystring)

    print(response.text)

    res = loads(response.text)
    df = pd.read_json(dumps(res))
    return df




#https://developers.google.com/custom-search/v1/reference/rest/v1/cse/list?apix_params=%7B%22cx%22%3A%220105d7b0bed374fee%22%2C%22imgSize%22%3A%22MEDIUM%22%2C%22num%22%3A5%2C%22q%22%3A%22image%20spiritual%20quote%20%22%7D
def getGoogleTest(query):
    import requests
    f = BASE_DIR + 'private.csv'

    df = pd.read_csv(f, header=None, index_col=False)
    df.columns = ['Name', 'Value']
    key = df.loc[df['Name'] == 'Google-API', 'Value'].values[0]
    engine = df.loc[df['Name'] == 'Google-Engine-ID', 'Value'].values[0]
    url = 'https://customsearch.googleapis.com/customsearch/v1'
    querystring = {"q": query, "key": key, "cx": engine,"num":"5"}
    response = requests.request("GET", url, params=querystring)

    print(response.text)
    return

'''
def generate_post(criteria, topic, max_length=None):
    import tokenizers
    print("Generating post on topic: " + topic)
    text = criteria + topic
    post = generator(text, max_length=max_length, do_sample=True, temperature=0.9,**encoded_input, pad_token_id=tokenizer.eos_token_id)[0]['generated_text']
    return post
'''
def pick_a_topic(m):
    return randint(1,m)

def run_bot():
    T_Bot = Twitter_Bot('David', ['spiritual', 'life', 'yoga', 'mindfulness' 'love'], 1)
    f = BASE_DIR + 'private.csv'

    df = pd.read_csv(f, header=None, index_col=False)
    df.columns = ['Name', 'Value']
    at = df.loc[df['Name'] == 'ACCESS_TOKEN', 'Value'].values[0]
    ats = df.loc[df['Name'] == 'ACCESS_TOKEN_SECRET', 'Value'].values[0]
    ck = df.loc[df['Name'] == 'CONSUMER_KEY', 'Value'].values[0]
    cks = df.loc[df['Name'] == 'CONSUMER_SECRET', 'Value'].values[0]

    api = T_Bot.twitterLogOn(
        ACCESS_TOKEN=at
        , ACCESS_TOKEN_SECRET=ats
        , CONSUMER_KEY=ck
        , CONSUMER_SECRET=cks
    )
    while True:
        index = pick_a_topic(3)
        topic_search = choice(T_Bot.bot_core_values)
        img_name = None
        df_quotes_index = 0

        if index == 1:
            post, img_name = getNews(topic_search)
        elif index == 2:
            hashtag = topic_search
            topic_search += ' quotes'
            post, img_name = getImages(topic_search)
            post += " #" +hashtag
        elif index == 3:
            if df_quotes_index > df_quotes.shape()[0]:
                df_quotes = getQuote(topic_search)
            q = df_quotes.iloc[df_quotes_index]['q']
            a = df_quotes.iloc[df_quotes_index]['a']
            p = 'Provided by https://zenquotes.io/'
            h = '#DaveTheBot #Automation #' +topic_search
            post = q + '\n' + a + '\n' + h + '\n\n' + p
            df_quotes_index += 1

        print("I am tweeting: " + post)
        T_Bot.post_tweets(api,post, img_name)

        sleep = choice(sleep_array)
        print('Waiting ' + str(sleep) + ' minutes.')
        time.sleep(sleep*60)



#https://developer.twitter.com/en/docs/twitter-api/tweets/search/integrate/build-a-query
#query = '(' + " OR ".join(T_Bot.bot_core_values) + ') (-has:links AND -is:retweet AND -is:reply AND -is:nullcast AND -has:mentions)'
#print(query)
#"#spiritual -filter:retweets"

#df = T_Bot.get_tweets(api, query, '2022-07-01', 100)
#rint('printing df')
#print(df)
#df.to_csv('/Users\etromp\Desktop\Bot\\test.csv')



if __name__ == "__main__":
    run_bot()




