import os
from time import sleep
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import re
import time
import datetime
import csv
try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse

class YoutubeChannelVideoScraper(object):

    def __init__(self):
        '''
        youtube_url
        '''
        # self.youtube_url = "https://www.youtube.com"
        # self.user_name = "EGA-CHANNEL1"
        # self.channel_videos_url = os.path.join(self.youtube_url, 'c', self.user_name, 'videos')
        '''
        csv_file_path
        '''
        # self.csv_file_name = "./data/youtube_channel_raw_data"
        # self.csv_file_path = os.path.join(os.getcwd(), self.csv_file_name+'.csv')
        '''
        extraction_data
        '''
        self.channel_videos_urls = []
        self.titles = []
        self.video_urls = []
        self.views = []
        self.channel_names = []
        self.channel_subscribers = []
        self.create_stamps = []
        self.mean_views = []
        self.mean_comparisons = []


    def run(self):
        self.read_channel_urls()
        self.get_page_source()
        self.parse_video_title_and_url_and_view()
        self.new_csv_file()
        self.save_as_csv_file()
        self.mean_view()
        self.mean_comparison()
        self.add_as_csv_file()
        self.driver.close()


    def read_channel_urls(self):
        channel_url_data = pd.read_csv('./data/youtube_channel_list.csv',index_col='channel_url')
        channel_urls_ndarray = channel_url_data.index.values
        channel_urls = channel_urls_ndarray.tolist()
        for i in channel_urls:
            youtube_url = 'https://www.youtube.com'
            self.channel_url = ('%s' % i)
            # videos_url = 'videos'
            channel_videos_url = urlparse.urljoin(youtube_url, self.channel_url+'/videos')
            self.channel_videos_urls.append(channel_videos_url)


    def get_page_source(self):
        self.driver = webdriver.Chrome()
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
                    '''
                    開発時に使用
                    '''
                    t = 0
                    start = time.time()
                    t = time.time() - start
                    t == 20
                    break
                else:
                    break


    def parse_video_title_and_url_and_view(self):
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
            channel_subscriber_sub = re.sub("\\D", "", str(channel_subscriber_replace))
            channel_subscriber_add_million = channel_subscriber_sub + '0000'
            channel_subscriber_material = int(channel_subscriber_add_million)
        else:
            channel_subscriber_replace = channel_subscriber_rstrip.replace(' ', '')
            channel_subscriber_sub = re.sub("\\D", "", str(channel_subscriber_replace))
            channel_subscriber_material = int(channel_subscriber_sub)
        for i in soup.find_all("a"):
            # title
            title = (i.get("title"))
            # url
            url = (i.get("href"))
            # view
            view_material_i = (i.get("aria-label"))
            # create_stamp
            create_stamp_material_i = (i.get("aria-label"))
            '''
            NoneExclusion
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
                self.views.append(view)
                self.channel_names.append(channel_name)
                self.channel_subscribers.append(channel_subscriber)
                self.create_stamps.append(create_stamp)


    def new_csv_file(self):
        today = datetime.date.today()
        channel_name = self.channel_name_rstrip
        self.new_csv_file_path = os.path.join('./data/'+channel_name+str(today)+'.csv')
        open('%s' % self.new_csv_file_path, 'w')


    def save_as_csv_file(self):
        data = {
         "title": self.titles,
         "url": self.video_urls,
         "view": self.views,
         "channel_name": self.channel_names,
         "channel_subscriber": self.channel_subscribers,
         "create_stamp": self.create_stamps
        }
        pd.DataFrame(data).to_csv(self.new_csv_file_path,index=False)


    def mean_view(self):
        df = pd.read_csv(self.new_csv_file_path)
        views = self.views
        s = sum(views)
        N = len(views)
        mean_view_material = s / N
        self.mean_view = round(mean_view_material)
        for i in views:
            self.mean_views.append(self.mean_view)


    def mean_comparison(self):
        df = pd.read_csv(self.new_csv_file_path)
        views = self.views
        mean_view = self.mean_views
        for i in views:
            mean_comparison_material = (i / self.mean_view) * 100
            mean_comparison = round(mean_comparison_material)
            self.mean_comparisons.append(mean_comparison)


    def add_as_csv_file(self):
        df = pd.read_csv(self.new_csv_file_path)
        df['mean_view'] = self.mean_views
        df['mean_comparison'] = self.mean_comparisons
        pd.DataFrame(df).to_csv(self.new_csv_file_path,index=False)


if __name__ == "__main__":
    scraper = YoutubeChannelVideoScraper()
    scraper.run()
    