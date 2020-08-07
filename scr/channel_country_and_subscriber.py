import os.path
from time import sleep
import datetime
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import re
import numpy as np
import regex
try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse


class ChannelCountryAndScraper(object):

    def __init__(self):
        self.channel_about_urls = []
        self.nihongo_channel_countries = []
        self.channel_subscribers_true = []
        self.channel_list_csv_file_name = "./../data/youtube_channel_list"
        self.channel_list_csv_file_path = os.path.join(os.getcwd(), self.channel_list_csv_file_name+'.csv')


    def run(self):
        self.read_channel_urls()
        self.get_page_source()
        self.channel_country_subscriber_add_as_csv_file()
        self.csv_file_drop_duplicate()
        self.driver.close()


    def read_channel_urls(self):
        df = pd.read_csv(self.channel_list_csv_file_path)
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
        self.driver = webdriver.Chrome()
        for i in self.channel_about_urls:
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
                html = self.driver.page_source
                if self.current_html != html:
                    self.current_html=html
                else:
                    self.parse_channel_country()
                    self.country_nihongo_true()
                    self.channel_subscriber_set()
                    break


    def parse_channel_country(self):
        self.channel_countries = []
        self.channel_subscribers = []
        soup = BeautifulSoup(self.current_html, 'html.parser')
        '''
        channelSubscriberOfIntExtractionFunction
        '''
        channel_subscriber_i = soup.find("yt-formatted-string", class_="style-scope ytd-c4-tabbed-header-renderer")
        channel_subscriber_lstrip = str(channel_subscriber_i).lstrip('<yt-formatted-string class="style-scope ytd-c4-tabbed-header-renderer" id="subscriber-count">')
        channel_subscriber_rstrip = channel_subscriber_lstrip.rstrip('</yt-formatted-string>')
        if "万" in channel_subscriber_rstrip:
            channel_subscriber_replace = channel_subscriber_rstrip.replace(' ', '')
            if "." in channel_subscriber_rstrip:
                s = float(channel_subscriber_rstrip.lstrip('チャンネル登録者数 ').rstrip('万人'))
                s_i, s_d = str(s).split('.')
                if 1 is len(s_d):
                    channel_subscriber_sub = re.sub("\\D", "", str(channel_subscriber_replace))
                    channel_subscriber_add_million = channel_subscriber_sub + '000'
                    channel_subscriber_material = int(channel_subscriber_add_million)
                elif 2 is len(s_d):
                    channel_subscriber_sub = re.sub("\\D", "", str(channel_subscriber_replace))
                    channel_subscriber_add_million = channel_subscriber_sub + '00'
                    channel_subscriber_material = int(channel_subscriber_add_million)
            else:
                channel_subscriber_sub = re.sub("\\D", "", str(channel_subscriber_replace))
                channel_subscriber_add_million = channel_subscriber_sub + '0000'
                channel_subscriber_material = int(channel_subscriber_add_million)
        elif "!--css-build:sh" in channel_subscriber_rstrip:
            channel_subscriber_material = "非表示"
        else:
            channel_subscriber_replace = channel_subscriber_rstrip.replace(' ', '')
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
            if "<!--css-build:shady-->" in str(country):
                country = None
            if "<" in str(country):
                country = None
            if "[]" in str(country):
                country = None
            self.channel_countries.append(country)
            self.channel_subscribers.append(channel_subscriber)


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


    def csv_file_drop_duplicate(self):
        df = pd.read_csv(self.channel_list_csv_file_path)
        df_drop_duplicate = df[df['channel_subscriber'].notnull()]
        pd.DataFrame(df_drop_duplicate).to_csv(self.channel_list_csv_file_path,index=False)
        print(self.channel_list_csv_file_path+"重複削除")


if __name__ == "__main__":
    channel_country = ChannelCountryAndScraper()
    channel_country.run()
