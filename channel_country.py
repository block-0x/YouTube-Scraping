import os.path
from time import sleep
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import re
import numpy as np
try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse
'''
pip install regex
'''
import regex


class ChannelCountryScraper(object):

    def __init__(self):
        self.channel_about_urls = []
        # self.channel_countries = []
        # self.channel_subscribers = []
        self.nihongo_channel_countries = []
        self.channel_subscribers_true = []


    def run(self):
        self.read_youtube_urls()
        self.get_page_source()
        # self.country_nihongo_true()
        self.channel_country_additional()
        self.channel_subscriber_additional()
        self.driver.close()


    def read_youtube_urls(self):
        channel_url_data = pd.read_csv('./data/youtube_channel_list.csv',index_col='channel_url')
        channel_urls_ndarray = channel_url_data.index.values
        channel_urls = channel_urls_ndarray.tolist()
        for i in channel_urls:
            youtube_url = 'https://www.youtube.com'
            self.channel_url = ('%s' % i)
            about_url = 'about'
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
            channel_subscriber_sub = re.sub("\\D", "", str(channel_subscriber_replace))
            channel_subscriber_add_million = channel_subscriber_sub + '00'
            channel_subscriber_material = int(channel_subscriber_add_million)
        elif "!--css-build:sh" in channel_subscriber_rstrip:
            channel_subscriber_material = None
        else:
            channel_subscriber_replace = channel_subscriber_rstrip.replace(' ', '')
            channel_subscriber_sub = re.sub("\\D", "", str(channel_subscriber_replace))
            channel_subscriber_material = int(channel_subscriber_sub)
            '''
            countryOfIntExtractionFunction
            '''
        for i in soup.find_all("td", class_="style-scope ytd-channel-about-metadata-renderer"):
            # i_x = ('{0}:{1}'.format(i, td_i[i]))
            country_i_findall = re.findall('<yt-formatted-string class="style-scope ytd-channel-about-metadata-renderer">.*</yt-formatted-string>', str(i))
            country_i_replace = str(country_i_findall).replace('<yt-formatted-string class="style-scope ytd-channel-about-metadata-renderer">', '').replace('</yt-formatted-string>', '')
            country = str(country_i_replace).replace("['", '').replace("']", '')
            # print(country)
            # print(country)
            # print(country)
            # country_item = country[i]
            # print(country_item)
            # country_index = ('{0}:{1}'.format(i, country))
            # print(country_index)
            # i_x = ('{0}:{1}'.format(i, td_i[i]))
            # print(country)
            '''
            channelSubscriberOfIntExtractionFunction
            '''
            channel_subscriber = channel_subscriber_material
            '''
            NoneExclusion
            '''
            if "<!--css-build:shady-->" in str(country):
                country = None
            if "<" in str(country):
                country = None
            if "[]" in str(country):
                country = None
            # if country is None:
            #     continue
            # if False in country:
            #     country = None
            # if str(country).isnumeric():
            #     country += country
            # if country == 0:
            #     country = None
            # if  is country:
            #     country = None
            # print(country)
            self.channel_countries.append(country)
            # self.country_nihongo_true()
            self.channel_subscribers.append(channel_subscriber)


    def country_nihongo_true(self):
        # print(self.channel_countries)
        country_list = self.channel_countries
        # print(country_list)
        # print(country_list)
        # print
        country_list_join = ','.join(str(country_list))
        country_list_join_replace = country_list_join.replace(',', '')
        # country_list_str_replace_list = (list(country_list_str_replace))
        # country_list_str_replace_findall = (re.findall('[ぁ-ゟ]+', str(country_list_str_replace_list)))
        # print(country_list_str_replace_findall)
        # print(country_list_str_replace)
        # print(('%s' % country_list_str_replace))
        # p = regex.compile(r'\p{Script_Extensions=Han}+')
        # print(p.fullmatch("NoneNone日本"))
        nihongo = regex.compile('[\u2E80-\u2FDF\u3005-\u3007\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF\U00020000-\U0002EBEF]+')
        country = (nihongo.findall(str(country_list_join_replace)))
        # print(country_list_join)
        if "[]" in str(country):
            country = '非表示'
        if "[" in str(country):
            country = str(country).replace("['", '').replace("']", '')
        # if "[" in str(country):
        #     country = ','.join(country).replace(',', '')
        # country
        self.nihongo_channel_countries.append(str(country))
        # print(self.nihongo_channel_countries)
        # print


    def channel_subscriber_set(self):
        subscriber_list =  self.channel_subscribers
        # subscriber_list_join = ','.join(str(subscriber_list))
        # subscriber_list_join_replace = subscriber_list_join.replace(',', '')
        subscriber = (list(set(subscriber_list)))
        # print(subscriber)
        # if "[]" in str(subscriber):
        #     subscriber = 0
        subscriber = str(subscriber).replace("[", '').replace("]", '')
        self.channel_subscribers_true.append(subscriber)



    def channel_country_additional(self):
        # print(str(self.channel_countries))
        df = pd.read_csv('./data/youtube_channel_list.csv')
        df['channel_country'] = self.nihongo_channel_countries
        pd.DataFrame(df).to_csv('./data/youtube_channel_list.csv',index=False)


    def channel_subscriber_additional(self):
        df = pd.read_csv('./data/youtube_channel_list.csv')
        df['channel_subscriber'] = self.channel_subscribers_true
        pd.DataFrame(df).to_csv('./data/youtube_channel_list.csv',index=False)


if __name__ == "__main__":
    channel_country = ChannelCountryScraper()
    channel_country.run()
