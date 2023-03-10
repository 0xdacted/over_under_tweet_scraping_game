import tweepy
import configparser
import pandas as pd
import json
import random

def read_config(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    return {
        'api_key': config['twitter']['api_key'],
        'api_key_secret': config['twitter']['api_key_secret'],
        'access_token': config['twitter']['access_token'],
        'access_token_secret': config['twitter']['access_token_secret'],
        'bearer_token': config['twitter']['bearer_token']
    }

def stream_tweets(bearer_token):
    class TweetPrinter(tweepy.StreamingClient):
        def __init__(self, bearer_token):
            super().__init__(bearer_token)
            self.columns = ['Tweet']
            self.data = []

        def on_data(self, data):
            json_data = json.loads(data)
            if '#' in json_data['data']['text']:
                self.data.append((json_data['data']['text']))

        def on_error(self, status):
            print(status)        

        def on_disconnect(self):
            df = pd.DataFrame(self.data, columns=self.columns)
            df.to_csv('tweets.csv', index=False)
            return super().on_disconnect()

    printer = TweetPrinter(bearer_token)
    printer.sample()

def analyze_tweets(file):
    df = pd.read_csv(file)
    hashtags = []
    for tweet in df['Tweet']:
        hashtags_in_tweet = [i for i in tweet.split() if i.startswith('#')]
        hashtags.extend(hashtags_in_tweet)

    hashtag_counts = pd.Series(hashtags).value_counts()
    sorted_hashtags = hashtag_counts.sort_values(ascending=False)
    top_1000_hashtags = sorted_hashtags[:1000]
    return top_1000_hashtags

def select_answer(df, hashtag1, hashtag2):
    print(f"Which of the following hashtags was tweeted more: {hashtag1} or {hashtag2}? Input '1', or '2 to select your answer.")
    user_choice = input()
    count1 = df[df['Hashtag'] == hashtag1]['Count'].values[0]
    count2 = df[df['Hashtag'] == hashtag2]['Count'].values[0]
    if user_choice == '1':
        if count1 > count2:
            print("Correct!")
            return True
        else:
            print(f"Incorrect. {hashtag2} was tweeted more ({count2} vs {count1}).")
            return False
    elif user_choice == '2':
        if count2 > count1:
            print("Correct!")
            return True
        else:
            print(f"Incorrect. {hashtag1} was tweeted more ({count1} vs {count2}).")
            return False
    else:
         print("Invalid option. Try again.")
         select_answer(df, hashtag1, hashtag2)


def main():
    
    choice = input("Enter 'G' to play the game, 'S' to stream tweets, 'A' to analyze tweets, or 'V' to view top 1000 hashtags: ")
    if choice == 'S' or choice == 's':
        config = read_config('config.ini')
        stream_tweets(config['bearer_token'])
    elif choice == 'A' or choice == 'a':
        top_1000_hashtags = analyze_tweets('tweets.csv')
        df = pd.DataFrame({'Hashtag': top_1000_hashtags.index, 'Count': top_1000_hashtags.values})
        df.to_csv('top_1000_hashtags.csv', index=False)
    elif choice == 'V' or choice == 'v':
        df = pd.read_csv('top_1000_hashtags.csv')
        print(df)
    elif choice == 'G' or choice == 'g':
        df = pd.read_csv('top_1000_hashtags.csv')
        used_hashtags = set()  
        score = 0
        while True:
            available_hashtags = set(df['Hashtag']) - used_hashtags
            if not available_hashtags:
                print(f"You have used all the hashtags. Your score is {score}")
                break
            hashtag1, hashtag2 = random.sample(list(available_hashtags), 2)
            used_hashtags.update({hashtag1, hashtag2})
            if select_answer(df, hashtag1, hashtag2):
                score += 1
            else:
                break
        print(f"Thanks for playing! Your final score is {score}")
    else:
        print("Invalid option. Try again.")
        main()
   
main()