import tweepy
import cv2
import urllib.request
from config import CONFIG
import find_mistakes
import processing
import shutil
import os

##### main関数 #####
def main(api):
   user_name, i = get_img(api) # 間違い探しをする画像の取得する
   processing.main(i) # 前処理を行う
   img1, img2 = set_img() # 添付画像の設定する
   find_mistakes.main(img1, img2) # 間違い探しを行う
   reply_img(api, user_name) # 間違い表示画像の返信する
   ### before ＆ after_imgの中身を空にする ###
   clean_file('before_img')
   clean_file('after_img')
   print('fin')

##### authの取得 #####
def get_auth():
   ### consumerキー、アクセストークン設定 ###
   CONSUMER_KEY = CONFIG["CONSUMER_KEY"]
   CONSUMER_SECRET = CONFIG["CONSUMER_SECRET"]
   ACCESS_KEY = CONFIG["ACCESS_KEY"]
   ACCESS_SECRET = CONFIG["ACCESS_SECRET"]
   ### 認証 ###
   auth = tweepy.OAuthHandler(CONSUMER_KEY,CONSUMER_SECRET)
   auth.set_access_token(ACCESS_KEY,ACCESS_SECRET)
   return auth

##### 間違い探しをする画像の取得 #####
def get_img(api):
   keyword = '@find_mistakes01 exclude:retweets' # キーワード
   for tweet in api.search(q = keyword, count = 50):
      user_name = tweet.user.screen_name # ユーザー名の取得
      ### 例外処理をする ###
      i = 1 # カウンター
      try:
         # ツイートを読み込む
         if 'media' in tweet.extended_entities:
            for media in tweet.extended_entities['media']:
               url = media['media_url_https'] # 画像のURLを取得
               print('get_img_success')
               download_img(url, i) # imgを保存
               i += 1
      except:
         print('error')
         pass
      return user_name, i-1

##### 添付画像の保存 #####
def download_img(url, i):
   file_name = 'before_img/img{}.png'.format(i) # ファイル指定
   urllib.request.urlretrieve(url, file_name) # ファイル保存
   print('download_img_success')

##### 添付画像の設定 #####
def set_img():
   ### 画像の読み込み ###
   img1 = cv2.imread('after_img/img1.png')
   img2 = cv2.imread('after_img/img2.png')
   print('set_img_success')
   return img1, img2

##### 間違い表示画像の返信 #####
def reply_img(api, user_name):
   message = '@{}'.format(user_name) # 返信先
   api.update_with_media(status = message, filename = 'after_img/mistakes.png') # ツイート
   print('reply_img_success')

##### before ＆ after_imgの中身を空にする #####
def clean_file(file_name):
   shutil.rmtree(file_name)
   os.mkdir(file_name)
   print('clean_file_success')