import os.path
from time import sleep
import datetime
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.common.keys import Keys
import re
import numpy as np
import regex
import json
import requests
try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse
import urllib.request, urllib.error
'''
proxy
'''
import socks, socket


class ChannelCountryAndScraper(object):

    def __init__(self):
        self.video_urls = []
        self.nihongo_channel_countries = []
        self.channel_subscribers_true = []
        self.channel_list_csv_file_name = "./../data/youtube_search_csv_data"
        self.channel_list_csv_file_path = os.path.join(os.getcwd(), self.channel_list_csv_file_name+'.csv')
        self.scarch_videos_list_csv_file_name = "./../data/scarch_videos_list_scv"
        self.scarch_videos_list_csv_file_path = os.path.join(os.getcwd(), self.scarch_videos_list_csv_file_name+'.csv')


    def run(self):
        self.copy_csv()
        self.csv_file_drop_duplicate()
        self.read_csv_urls()
        self.get_page_source()
        # self.parse_video_show()
        # self.csv_file_drop_duplicate()
        # self.driver.close()


    def copy_csv(self):
        df = pd.read_csv(self.channel_list_csv_file_path)
        pd.DataFrame(df).to_csv(self.scarch_videos_list_csv_file_path,index=False)
        print(self.scarch_videos_list_csv_file_path+"にコピーしました")


    def csv_file_drop_duplicate(self):
        df = pd.read_csv(self.scarch_videos_list_csv_file_path)
        df_drop_duplicate = df.drop_duplicates(subset='video_url', keep='last')
        self.df_add_csv = pd.DataFrame(df_drop_duplicate).to_csv(self.scarch_videos_list_csv_file_path,index=False)
        print(self.scarch_videos_list_csv_file_path+"重複動画削除")


    def read_csv_urls(self):
        df = pd.read_csv(self.scarch_videos_list_csv_file_path,index_col='video_url')
        video_url_data = df.index.values
        video_urls = video_url_data.tolist()
        for i in video_urls:
            youtube_url = 'https://www.youtube.com'
            self.video_url = ('%s' % i)
            video_url_path = urlparse.urljoin(youtube_url, self.video_url)
            self.video_urls.append(video_url_path)


    def get_page_source(self):
        for i in self.video_urls:
            html = requests.get('http://localhost:8050/render.html',
            params={'url': i, 'wait': 0.5})
            self.soup = BeautifulSoup(html.text, "html.parser")
            self.parse_view_and_createAt()
            self.parse_video_tags()
            self.parse_video_description()
            self.parse_video_like()



    def parse_view_and_createAt(self):
        self.views = []
        self.create_ats = []
        for i in self.soup.find_all('div', {"class" : "style-scope ytd-video-primary-info-renderer"}):
            view_i = re.findall('</ytd-badge-supported-renderer><div class="style-scope ytd-video-primary-info-renderer" id="info"><div class="style-scope ytd-video-primary-info-renderer" id="info-text"><div class="style-scope ytd-video-primary-info-renderer" id="count"><yt-view-count-renderer class="style-scope ytd-video-primary-info-renderer" small_=""><!--css-build:shady--><span class="view-count style-scope yt-view-count-renderer">.*</span><span class="short-view-count style-scope yt-view-count-renderer">', str(i))
            view_i_join = ",".join(view_i)
            view_i_join_replace = str(view_i_join).replace('</ytd-badge-supported-renderer><div class="style-scope ytd-video-primary-info-renderer" id="info"><div class="style-scope ytd-video-primary-info-renderer" id="info-text"><div class="style-scope ytd-video-primary-info-renderer" id="count"><yt-view-count-renderer class="style-scope ytd-video-primary-info-renderer" small_=""><!--css-build:shady--><span class="view-count style-scope yt-view-count-renderer">', '').replace(' views</span><span class="short-view-count style-scope yt-view-count-renderer">', '')
            view = view_i_join_replace.replace(',', '')
            create_at_i = re.findall('views</span></yt-view-count-renderer></div><div class="style-scope ytd-video-primary-info-renderer" id="date"><span class="style-scope ytd-video-primary-info-renderer" id="dot">•</span><yt-formatted-string class="style-scope ytd-video-primary-info-renderer">.*</yt-formatted-string>', str(i))
            create_at_i_join = ",".join(create_at_i)
            create_at = create_at_i_join.replace('views</span></yt-view-count-renderer></div><div class="style-scope ytd-video-primary-info-renderer" id="date"><span class="style-scope ytd-video-primary-info-renderer" id="dot">•</span><yt-formatted-string class="style-scope ytd-video-primary-info-renderer">', '').replace('</yt-formatted-string>', '')
            if view is None:
                continue
            if create_at is None:
                continue
            if not view == '':
                self.views.append(view)
                self.create_ats.append(create_at)
                print('parse_view_and_createAt complete')


    def parse_video_tags(self):
        self.tags = []
        for i in self.soup.find_all('meta'):
            tag_i = re.findall('<meta content.*property="og:video:tag"/>', str(i))
            tag_i_join = ",".join(tag_i)
            tag = tag_i_join.replace('<meta content="', '').replace('" property="og:video:tag"/>', '')
            if tag is None:
                continue
            if not tag == '':
                self.tags.append(tag)
                print('tag complete')


    def parse_video_description(self):
        self.descriptions = []
        for i in self.soup.find_all('meta'):
            description_i = re.findall('<meta content.*property="og:description"/>', str(i))
            description_i_join = ",".join(description_i)
            description = description_i_join.replace('<meta content="', '').replace('" property="og:description"/>', '')
            if description is None:
                continue
            if not description == '':
                self.descriptions.append(description)
                print('description complete')


    def parse_video_like(self):
        self.likes = []
        self.dislikes = []
        for i in self.soup.find_all('yt-formatted-string'):
            like_i = re.findall('aria-label.* likes', str(i))
            like_i_join = ",".join(like_i)
            like = like_i_join.replace('aria-label="', '').replace(' likes', '')
            dislike_i = re.findall('aria-label.*dislikes', str(i))
            dislike_i_join = ",".join(dislike_i)
            dislike = dislike_i_join.replace('aria-label="', '').replace(' dislikes', '')
            if like is None:
                continue
            if dislike is None:
                continue
            if not like == '':
                self.likes.append(like)
                print('like complete')
            if not dislike == '':
                self.dislikes.append(dislike)
                print('dislike complete')


    def country_nihongo_true(self):
        country_list = self.channel_countries
        country_list_join = ','.join(str(country_list))
        country_list_join_replace = country_list_join.replace(',', '')
        nihongo = regex.compile('[\u2E80-\u2FDF\u3005-\u3007\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF\U00020000-\U0002EBEF]+')
        country = (nihongo.findall(str(country_list_join_replace)))
        if "[]" in str(country):
            country = '非表示'
        if "[" in str(country):
            country = str(country).replace("['", '').replace("']", '')
        self.nihongo_channel_countries.append(str(country))


    def channel_subscriber_set(self):
        subscriber_list =  self.channel_subscribers
        subscriber = (list(set(subscriber_list)))
        subscriber = str(subscriber).replace("[", '').replace("]", '')
        self.channel_subscribers_true.append(subscriber)


    def channel_country_subscriber_add_as_csv_file(self):
        df = self.df_update
        df['channel_country'] = self.nihongo_channel_countries
        df['channel_subscriber'] = self.channel_subscribers_true
        pd.DataFrame(df).to_csv(self.channel_list_csv_file_path, mode='a', header=False,index=False)
        print(self.channel_list_csv_file_path+"国・登録者追記")


    # def csv_file_drop_duplicate(self):
        df = pd.read_csv(self.channel_list_csv_file_path)
        df_drop_duplicate = df[df['channel_subscriber'].notnull()]
        pd.DataFrame(df_drop_duplicate).to_csv(self.channel_list_csv_file_path,index=False)
        print(self.channel_list_csv_file_path+"重複削除")


if __name__ == "__main__":
    channel_country = ChannelCountryAndScraper()
    channel_country.run()
