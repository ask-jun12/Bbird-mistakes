# tweepyでのストリーミング（リアルタイムでのツイートの取得）
import tweepy
from config import CONFIG
import twitter_bot

##### 呪文 #####
auth = twitter_bot.get_auth()
api = tweepy.API(auth, wait_on_rate_limit = True)

##### main関数 #####
def main():
   myStreamListener = MyStreamListener() # オブジェクト作成、インスタンス化
   myStream = tweepy.Stream(auth = api.auth, listener=myStreamListener)
   myStream.filter(track=['@find_mistakes01']) # filter word

##### StreamListenerの作成 #####
# override tweepy.StreamListener to add logic to on_status
class MyStreamListener(tweepy.StreamListener):
   def on_status(self, status):
      print("name : %s, screen_name : %s" % (status.user.name, status.user.screen_name))
      print("text : %s " % status.text)
      print("-"*50)
      twitter_bot.main(api)

   ### エラー処理 ###
   # 時間枠内にストリーミングAPIの接続回数を上回った場合、420エラー
   def on_error(self, status_code):
      if status_code == 420:
         return False

# ctrl + c で終了
if __name__ == '__main__':
   main()