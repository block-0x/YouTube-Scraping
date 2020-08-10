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
        self.parse_video_show()
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
        socks.set_default_proxy(socks.PROXY_TYPE_SOCKS5, '127.0.0.1', 9050)
        socket.socket = socks.socksocket
        for i in self.video_urls:
            html = urllib.request.urlopen(i)
            self.soup = BeautifulSoup(html, "html.parser")
            print(self.soup)


    def parse_video_show(self):
        for i in self.soup.find_all("div", class_="style-scope ytd-video-primary-info-renderer"):
            print(i)
            # country_i_findall = re.findall('<yt-formatted-string class="style-scope ytd-channel-about-metadata-renderer">.*</yt-formatted-string>', str(i))
            # country_i_replace = str(country_i_findall).replace('<yt-formatted-string class="style-scope ytd-channel-about-metadata-renderer">', '').replace('</yt-formatted-string>', '')
            # country = str(country_i_replace).replace("['", '').replace("']", '')
            # '''
            # channelSubscriberOfIntExtractionFunction
            # '''
            # channel_subscriber = channel_subscriber_material
            # '''
            # Validation
            # '''
            # if "<!--css-build:shady-->" in str(country):
            #     country = None
            # if "<" in str(country):
            #     country = None
            # if "[]" in str(country):
            #     country = None
            # self.channel_countries.append(country)
            # self.channel_subscribers.append(channel_subscriber)


    # def parse_tags(self):
    #     for i in self.soup.re.findall('<meta content="YouTube" property="og:site_name"/>.*<div class="skeleton flexy" id="player">'):



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
