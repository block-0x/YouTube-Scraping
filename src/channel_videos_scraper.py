import os
import os.path
from time import sleep
import pandas as pd
import numpy as np
import regex
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import re
import time
import datetime
import datetime as dt
import requests
import csv
try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse
# import sys
# sys.path.append(os.path.channel_country_and_subscriberpath(".."))
# from . import channel_country_and_subscriber
# import socks, socket

# socks.set_default_proxy(socks.PROXY_TYPE_SOCKS5, '127.0.0.1', 9050)
# socket.socket = socks.socksocket

class YoutubeChannelVideoScraper(object):

    def __init__(self):
        self.channel_videos_urls = []
        self.mean_views_all = []
        self.channel_list_csv_file_name = "./../data/channel/youtube_channel_list"
        self.channel_list_csv_file_path = os.path.join(os.getcwd(), self.channel_list_csv_file_name+'.csv')


    def run(self):
        self.drop_channel_list_duplicate()
        self.new_dir()
        self.scrape_at_filter()
        '''
        全てのデータを更新する際に使用
        '''
        # self.read_channel_urls()
        self.get_page_source()
        self.channel_list_add_as_csv_file()
        self.csv_file_drop_duplicate()
        self.driver.close()


    def drop_channel_list_duplicate(self):
        df = pd.read_csv(self.channel_list_csv_file_name, engine='python')
        df_drop_duplicate = df.drop_duplicates(subset='channel_url', keep='last')
        pd.DataFrame(df_drop_duplicate).to_csv(self.channel_list_csv_file_path,index=False, engine='python')
        print(self.channel_list_csv_file_path+"重複削除しました")


    def new_dir(self):
        today = datetime.date.today()
        dt_now = datetime.datetime.now()
        hour = dt_now.hour
        minute = dt_now.minute
        self.new_dir_path = os.path.join('./../data/channel_videos/'+str(today)+'-'+str(hour)+':'+str(minute)+'channel_videos')
        os.mkdir(self.new_dir_path)
        print("新規ファイル作成しました")


    def scrape_at_filter(self):
        df = pd.read_csv(self.channel_list_csv_file_path, engine='python')
        self.df_scrape_at_this_month = df[df['scrape_at'] > dt.datetime(2020,8,13).strftime("%Y/%m/%d")]
        channel_url_data = self.df_scrape_at_this_month.set_index('channel_url')
        channel_urls_ndarray = channel_url_data.index.values
        channel_urls = channel_urls_ndarray.tolist()
        for i in channel_urls:
            youtube_url = 'https://www.youtube.com'
            self.channel_url = ('%s' % i)
            channel_video_url = urlparse.urljoin(youtube_url, self.channel_url+'/videos')
            self.channel_videos_urls.append(channel_video_url)


    '''
    all data udpate
    '''
    def read_channel_urls(self):
        channel_url_data = pd.read_csv(self.channel_list_csv_file_path, index_col='channel_url', engine='python')
        channel_urls_ndarray = channel_url_data.index.values
        channel_urls = channel_urls_ndarray.tolist()
        for i in channel_urls:
            youtube_url = 'https://www.youtube.com'
            self.channel_url = ('%s' % i)
            channel_videos_url = urlparse.urljoin(youtube_url, self.channel_url+'/videos')
            self.channel_videos_urls.append(channel_videos_url)


    def get_page_source(self):
        self.driver = webdriver.Firefox()
        for i in self.channel_videos_urls:
            self.driver.get(i)
            self.current_html = self.driver.page_source
            element = self.driver.find_element_by_xpath('//*[@class="style-scope ytd-page-manager"]')
            actions = ActionChains(self.driver)
            actions.move_to_element(element)
            actions.perform()
            actions.reset_actions()
            while True:
                for j in range(100):
                    actions.send_keys(Keys.PAGE_DOWN)
                actions.perform()
                sleep(2)
                html = self.driver.page_source
                if self.current_html != html:
                    self.current_html=html
                    # t = 0
                    # start = time.time()
                    # t = time.time() - start
                    # t == 10
                    # self.parse_videos_title_and_url_and_view()
                    # self.new_csv_file()
                    # self.save_as_csv_file()
                    # self.mean_view_function()
                    # self.mean_views_append()
                    # self.mean_comparison_function()
                    # self.add_as_csv_file()
                    # break
                else:
                    self.parse_videos_title_and_url_and_view()
                    self.new_csv_file()
                    self.save_as_csv_file()
                    self.mean_view_function()
                    self.mean_views_append()
                    self.mean_comparison_function()
                    self.add_as_csv_file()
                    break


    def parse_videos_title_and_url_and_view(self):
        self.titles = []
        self.video_urls = []
        self.views = []
        self.channel_names = []
        self.channel_subscribers = []
        self.create_stamps = []
        soup = BeautifulSoup(self.current_html, 'html.parser')
        '''
        ChannelNameOfExtractionFunction
        '''
        channel_name_i = soup.find("yt-formatted-string", class_="style-scope ytd-channel-name")
        channel_name_lstrip = str(channel_name_i).lstrip('<yt-formatted-string class="style-scope ytd-channel-name" id="text" title="">')
        channel_name_rstrip = channel_name_lstrip.rstrip('</yt-formatted-string>')
        self.channel_name_rstrip = str(channel_name_rstrip)
        '''
        ChannelSubscriberOfIntExtractionFunction
        '''
        channel_subscriber_i = soup.find("yt-formatted-string", class_="style-scope ytd-c4-tabbed-header-renderer")
        channel_subscriber_lstrip = str(channel_subscriber_i).lstrip('<yt-formatted-string class="style-scope ytd-c4-tabbed-header-renderer" id="subscriber-count">')
        channel_subscriber_rstrip = channel_subscriber_lstrip.rstrip('</yt-formatted-string>')
        if "万" in channel_subscriber_rstrip:
            channel_subscriber_replace = channel_subscriber_rstrip.replace(' ', '')
            if "." in channel_subscriber_rstrip:
                channel_subscriber_sub = re.sub("\\D", "", str(channel_subscriber_replace))
                channel_subscriber_add_million = channel_subscriber_sub + '00'
                channel_subscriber_material = int(channel_subscriber_add_million)
            else:
                channel_subscriber_sub = re.sub("\\D", "", str(channel_subscriber_replace))
                channel_subscriber_add_million = channel_subscriber_sub + '0000'
                channel_subscriber_material = int(channel_subscriber_add_million)
        elif "!--css-build:sh" in channel_subscriber_rstrip:
            channel_subscriber_material = None
        else:
            channel_subscriber_replace = channel_subscriber_rstrip.replace(' ', '')
            channel_subscriber_sub = re.sub("\\D", "", str(channel_subscriber_replace))
            channel_subscriber_material = int(channel_subscriber_sub)
        for i in soup.find_all("a"):
            title = (i.get("title"))
            url = (i.get("href"))
            view_material_i = (i.get("aria-label"))
            create_stamp_material_i = (i.get("aria-label"))
            '''
            Validation
            '''
            if title is None:
                continue
            elif url is None:
                continue
            elif view_material_i is None:
                continue
            elif create_stamp_material_i is None:
                continue
            '''
            ViewOfIntExtractionFunction
            '''
            view_material = view_material_i.replace('　', ' ')
            view_findall = (re.findall('前 .*回視聴', view_material))
            if view_findall:
                view_str = ",".join(view_findall)
                view_replace_x = view_str.replace('前 ', '')
                view_replace_x_x = view_replace_x.replace(' 回視聴', '')
                view_replace_x_x_x = view_replace_x_x.replace(',', '')
                view_int = [int(s) for s in view_replace_x_x_x.split() if s.isdigit()]
                view_last_int = (view_int[-1])
                view = view_last_int
            '''
            ChannelInfomation
            '''
            channel_name = str(channel_name_rstrip)
            channel_subscriber = channel_subscriber_material
            '''
            CreatAtOfIntExtractionFunction
            '''
            create_stamp_material = (i.get("aria-label"))
            create_stamp_findall = (re.findall('%s .*前' % channel_name, create_stamp_material))
            create_stamp_str = ",".join(create_stamp_findall)
            create_stamp_replace_x = create_stamp_str.replace(channel_name, '')
            create_stamp_replace_x_x = create_stamp_replace_x.replace(' ', '')
            create_stamp = create_stamp_replace_x_x
            if "/watch?v=" in url:
                self.titles.append(title)
                self.video_urls.append(url)
                try:
                    self.views.append(view)
                except UnboundLocalError:
                    view = None
                    self.views.append(view)
                    print("parse_videos_title_and_url_and_viewエラー")
                    pass
                print(channel_name)
                self.channel_names.append(channel_name)
                print(channel_subscriber)
                self.channel_subscribers.append(channel_subscriber)
                self.create_stamps.append(create_stamp)


    def new_csv_file(self):
        today = datetime.date.today()
        channel_name_material = self.channel_name_rstrip
        channel_name = channel_name_material.replace("/", "")
        self.new_csv_file_path = os.path.join(self.new_dir_path+'/'+channel_name+str(today)+'.csv')
        open('%s' % self.new_csv_file_path, 'w')
        print("新規ファイル作成しました")


    def save_as_csv_file(self):
        if None in self.views:
            pass
        data = {
         "title": self.titles,
         "url": self.video_urls,
         "view": self.views,
         "channel_name": self.channel_names,
         "channel_subscriber": self.channel_subscribers,
         "create_stamp": self.create_stamps
        }
        pd.DataFrame(data).to_csv(self.new_csv_file_path,index=False, engine='python')
        print("新規ファイルに保存しました")


    def mean_view_function(self):
        self.mean_views = []
        if None in self.views:
            pass
        df = pd.read_csv(self.new_csv_file_path, engine='python')
        try:
            views = self.views
            s = sum(views)
            N = len(views)
            self.mean_view_material = s / N
            self.mean_view = round(self.mean_view_material)
            for i in views:
                self.mean_views.append(self.mean_view)
        except ValueError:
            print('mean_view_function: ValueError')
        except TypeError:
            print('mean_view_function: TypeError')


    def mean_views_append(self):
        mean_views_round = round(self.mean_view_material)
        print(mean_views_round)
        mean_views = (str(mean_views_round))
        print(mean_views)
        self.mean_views_all.append(mean_views)
        print(mean_views)


    def mean_comparison_function(self):
        self.mean_comparisons = []
        if None in self.views:
            pass
        df = pd.read_csv(self.new_csv_file_path, engine='python')
        views = self.views
        mean_view = self.mean_views
        for i in views:
            try:
                mean_comparison_material = (i / self.mean_view) * 100
                mean_comparison = round(mean_comparison_material)
                self.mean_comparisons.append(mean_comparison)
            except AttributeError:
                print('mean_comparison_function: AttributeError')
            except TypeError:
                print('mean_comparison_function: TypeError')
            except ValueError:
                print('mean_comparison_function: ValueError')


    def add_as_csv_file(self):
        if None in self.views:
            pass
        df = pd.read_csv(self.new_csv_file_path, engine='python')
        try:
            df['mean_view'] = self.mean_views
        except ValueError:
            print('add_as_csv_file: ValueError')
        try:
            df['mean_comparison'] = self.mean_comparisons
        except ValueError:
            print('add_as_csv_file: ValueError')
        pd.DataFrame(df).to_csv(self.new_csv_file_path,index=False, engine='python')
        print(self.new_csv_file_path+"データを保存しました")


    def  channel_list_add_as_csv_file(self):
        this_month_filter_df = self.df_scrape_at_this_month
        print(self.mean_views_all)
        this_month_filter_df['mean_view'] = self.mean_views_all
        pd.DataFrame(this_month_filter_df).to_csv(self.channel_list_csv_file_path, mode='a', header=False,index=False, engine='python')
        print(self.channel_list_csv_file_path+"追記しました")


    def csv_file_drop_duplicate(self):
        df = pd.read_csv(self.channel_list_csv_file_path, engine='python')
        df_drop_duplicate = df.drop_duplicates(subset='channel_url', keep='last')
        df_add_csv = pd.DataFrame(df_drop_duplicate).to_csv(self.channel_list_csv_file_path,index=False, engine='python')
        print(self.channel_list_csv_file_path+"重複削除しました")


class YoutubeChannelOverviewScraper(object):

    def __init__(self):
        self.channel_about_urls = []
        self.channel_subscribers_length = []
        self.channel_length = []
        self.channel_list_csv_file_name = "./../data/channel/youtube_channel_list"
        self.channel_list_csv_file_path = os.path.join(os.getcwd(), self.channel_list_csv_file_name+'.csv')
        '''
        scraper JapaneWebScraper
        '''
        # self.nihongo_channel_countries = []


    def run(self):
        self.scrape_at_filter()
        '''
        All data update
        '''
        # self.read_channel_urls()
        self.get_page_source()
        self.channel_country_subscriber_add_as_csv_file()
        self.csv_file_drop_duplicate()


    def scrape_at_filter(self):
        df = pd.read_csv(self.channel_list_csv_file_path, engine='python')
        self.df_scrape_at_this_month = df[df['scrape_at'] > dt.datetime(2020,8,13).strftime("%Y/%m/%d")]
        channel_url_data = self.df_scrape_at_this_month.set_index('channel_url')
        channel_urls_ndarray = channel_url_data.index.values
        channel_urls = channel_urls_ndarray.tolist()
        print(channel_urls)
        for i in channel_urls:
            youtube_url = 'https://www.youtube.com'
            self.channel_url = ('%s' % i)
            channel_about_url = urlparse.urljoin(youtube_url, self.channel_url+'/about')
            self.channel_about_urls.append(channel_about_url)
            print(self.channel_about_urls[-1])


    '''
    All data update
    '''
    def read_channel_urls(self):
        df = pd.read_csv(self.channel_list_csv_file_path, engine='python')
        self.df_update = df[df['channel_subscriber'].isnull()]
        channel_url_data = self.df_update.set_index('channel_url')
        channel_urls_ndarray = channel_url_data.index.values
        channel_urls = channel_urls_ndarray.tolist()
        for i in channel_urls:
            youtube_url = 'https://www.youtube.com'
            self.channel_url = ('%s' % i)
            channel_about_url = urlparse.urljoin(youtube_url, self.channel_url+'/about')
            self.channel_about_urls.append(channel_about_url)


    def get_page_source(self):
        for i in self.channel_about_urls:
            html = requests.get('http://localhost:8050/render.html',
            params={'url': i, 'wait': 5})
            self.soup = BeautifulSoup(html.text, "html.parser")
            self.parse_channel_country()
            self.country_set()
            '''
            scraper JapaneWebScraper
            '''
            # self.country_nihongo_true()
            self.channel_subscriber_set()


    def parse_channel_country(self):
        self.channel_countries = []
        self.channel_subscribers = []
        soup = self.soup
        '''
        channelSubscriberOfIntExtractionFunction
        '''
        channel_subscriber_i = soup.find("yt-formatted-string", class_="style-scope ytd-c4-tabbed-header-renderer")
        channel_subscriber_lstrip = str(channel_subscriber_i).lstrip('<yt-formatted-string class="style-scope ytd-c4-tabbed-header-renderer" id="subscriber-count">')
        channel_subscriber_rstrip = channel_subscriber_lstrip.rstrip('</yt-formatted-string>')
        if "K" in channel_subscriber_rstrip:
            channel_subscriber_replace = channel_subscriber_rstrip.replace(' ', '')
            if "." in channel_subscriber_rstrip:
                s = float(str(channel_subscriber_rstrip).rstrip('K subscrib'))
                s_i, s_d = str(s).split('.')
                if 1 is len(s_d):
                    channel_subscriber_sub = re.sub("\\D", "", str(channel_subscriber_replace))
                    channel_subscriber_add_million = str(channel_subscriber_sub) + '00'
                    channel_subscriber_material = int(channel_subscriber_add_million)
                elif 2 is len(s_d):
                    channel_subscriber_sub = re.sub("\\D", "", str(channel_subscriber_replace))
                    channel_subscriber_add_million = str(channel_subscriber_sub) + '0'
                    channel_subscriber_material = int(channel_subscriber_add_million)
            else:
                channel_subscriber_sub = re.sub("\\D", "", str(channel_subscriber_replace))
                channel_subscriber_add_million = str(channel_subscriber_sub) + '000'
                channel_subscriber_material = int(channel_subscriber_add_million)
        elif "M" in channel_subscriber_rstrip:
            channel_subscriber_replace = channel_subscriber_rstrip.replace(' ', '')
            if "." in channel_subscriber_rstrip:
                s = float(str(channel_subscriber_rstrip).rstrip('M subscrib'))
                s_i, s_d = str(s).split('.')
                if 1 is len(s_d):
                    channel_subscriber_sub = re.sub("\\D", "", str(channel_subscriber_replace))
                    channel_subscriber_add_million = str(channel_subscriber_sub) + '00000'
                    channel_subscriber_material = int(channel_subscriber_add_million)
                elif 2 is len(s_d):
                    channel_subscriber_sub = re.sub("\\D", "", str(channel_subscriber_replace))
                    channel_subscriber_add_million = str(channel_subscriber_sub) + '0000'
                    channel_subscriber_material = int(channel_subscriber_add_million)
                else:
                    channel_subscriber_sub = re.sub("\\D", "", str(channel_subscriber_replace))
                    channel_subscriber_add_million = str(channel_subscriber_sub) + '000000'
                    channel_subscriber_material = int(channel_subscriber_add_million)
        elif "--" in channel_subscriber_rstrip:
            channel_subscriber_material = "非表示"
        else:
            channel_subscriber_replace = channel_subscriber_rstrip.rstrip('K subscrib')
            channel_subscriber_sub = re.sub("\\D", "", str(channel_subscriber_replace))
            channel_subscriber_material = int(channel_subscriber_sub)
            '''
            countryOfIntExtractionFunction
            '''
        for i in soup.find_all("td", class_="style-scope ytd-channel-about-metadata-renderer"):
            country_i_findall = re.findall('<yt-formatted-string class="style-scope ytd-channel-about-metadata-renderer">.*</yt-formatted-string>', str(i))
            country_i_replace = str(country_i_findall).replace('<yt-formatted-string class="style-scope ytd-channel-about-metadata-renderer">', '').replace('</yt-formatted-string>', '')
            country = str(country_i_replace).replace("['", '').replace("']", '')
            '''
            channelSubscriberOfIntExtractionFunction
            '''
            channel_subscriber = channel_subscriber_material
            '''
            Validation
            '''
            if "--" in str(country):
                country = '非表示'
            if "<" in str(country):
                country = '非表示'
            if "[]" in str(country):
                country = '非表示'
            if None is channel_subscriber:
                channel_subscriber = '非表示'
            self.channel_countries.append(country)
            self.channel_subscribers.append(channel_subscriber)


    '''
    scraper JapaneseWebScraper
    '''
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


    def country_set(self):
        countries = self.channel_countries
        countries_join = (''.join(countries))
        p = re.compile('[a-zA-Z]+')
        country = ''.join(p.findall(countries_join))
        if None is country:
            country = '非表示'
        self.channel_length.append(country)


    def channel_subscriber_set(self):
        subscribers =  self.channel_subscribers
        subscriber = str(list(set(subscribers))).replace("[", '').replace("]", '').replace("'", '')
        self.channel_subscribers_length.append(subscriber)


    def channel_country_subscriber_add_as_csv_file(self):
        df = self.df_scrape_at_this_month
        print(self.channel_length)
        print(self.channel_subscribers_length)
        df['channel_country'] = self.channel_length
        df['channel_subscriber'] = self.channel_subscribers_length
        pd.DataFrame(df).to_csv(self.channel_list_csv_file_path, mode='a', header=False,index=False, engine='python')
        print(self.channel_list_csv_file_path+"国・登録者を更新しました")


    def csv_file_drop_duplicate(self):
        df = pd.read_csv(self.channel_list_csv_file_path, engine='python')
        df_drop_duplicate = df[df['channel_subscriber'].notnull()]
        pd.DataFrame(df_drop_duplicate).to_csv(self.channel_list_csv_file_path,index=False, engine='python')
        print(self.channel_list_csv_file_path+"重複削除しました")


if __name__ == "__main__":
    scraper = YoutubeChannelVideoScraper()
    scraper.run()
    scraper = YoutubeChannelOverviewScraper()
    scraper.run()

