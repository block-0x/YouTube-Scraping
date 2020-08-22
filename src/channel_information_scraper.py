from bs4 import BeautifulSoup
import datetime
import datetime as dt
import json
import os.path
import pandas as pd
import re
import regex
import requests
from time import sleep
import numpy as np
try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse
import urllib.request, urllib.error


class YoutubeChannelInformationScraper(object):

    def __init__(self):
        self.channel_about_urls = []
        self.channel_list_update_csv_file_name = "./../data/channel/youtube_channel_list_update"
        self.channel_list_csv_update_file_path = os.path.join(os.getcwd(), self.channel_list_update_csv_file_name+'.csv')
        '''
        scraper JapaneWebScraper
        '''
        # self.nihongo_channel_countries = []


    def run(self):
        self.drop_channel_list_duplicate()
        self.scrape_at_filter()
        '''
        All data update
        '''
        # self.read_channel_urls()
        self.get_page_source()
        self.drop_channel_list_duplicate()


    def drop_channel_list_duplicate(self):
        df = pd.read_csv(self.channel_list_csv_update_file_path, engine='python')
        df_drop_duplicate = df.drop_duplicates(subset='channel_url', keep='last')
        pd.DataFrame(df_drop_duplicate).to_csv(self.channel_list_csv_update_file_path,index=False)
        print("重複削除しました")


    def scrape_at_filter(self):
        self.df = pd.read_csv(self.channel_list_csv_update_file_path, engine='python')
        self.df_scrape_at_this_month = self.df[self.df['scrape_at'] > dt.datetime(2020,8,19).strftime("%Y/%m/%d")]
        channel_url_data = self.df_scrape_at_this_month.set_index('channel_url')
        channel_urls_ndarray = channel_url_data.index.values
        channel_urls = channel_urls_ndarray.tolist()
        for i in channel_urls:
            youtube_url = 'https://www.youtube.com'
            self.channel_url = ('%s' % i)
            channel_about_url = urlparse.urljoin(youtube_url, self.channel_url+'/about')
            self.channel_about_urls.append(channel_about_url)


    '''
    All data update
    '''
    def read_channel_urls(self):
        df = pd.read_csv(self.channel_list_csv_update_file_path, engine='python')
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
            self.parse_channel_country_subscriber()
            self.parse_channel_create_at()
            self.parse_channel_all_video_views()
            self.channel_social_links()
            self.country_set()
            '''
            scraper JapaneWebScraper
            '''
            # self.country_nihongo_true()
            self.channel_subscriber_set()
            self.channel_list_csv_scarch_column()
            self.country_subscriber_add_as_csv_file()


    def parse_channel_country_subscriber(self):
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
            try:
                channel_subscriber_material = int(channel_subscriber_sub)
            except ValueError:
                channel_subscriber_material = "非表示"
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
            if "--" or "<" or "[]" in str(country):
                country = '非表示'
            if None is channel_subscriber:
                channel_subscriber = '非表示'
            self.channel_countries.append(country)
            self.channel_subscribers.append(channel_subscriber)


    def parse_channel_create_at(self):
        self.channel_create_at = []
        soup = self.soup.find_all('span', {"class" : "style-scope yt-formatted-string"})
        for i in soup:
	        channel_create_at_i = re.findall('<span class="style-scope yt-formatted-string" dir="auto">.*</span>', str(i))
	        channel_create_at_str = str(channel_create_at_i).replace('<span class="style-scope yt-formatted-string" dir="auto">', '').replace('</span>', '')
	        if "," in str(channel_create_at_str):
	        	channel_create_at_str_replace = str(channel_create_at_str).replace(',', '').replace("['", '').replace("']", '')
		        channel_create_at = datetime.datetime.strptime(str(channel_create_at_str_replace), '%b %d %Y').strftime('%Y/%m/%d')
		        self.channel_create_at.append(channel_create_at)


    def parse_channel_all_video_views(self):
        self.channel_all_video_views = []
        soup = self.soup.find_all('yt-formatted-string', {"class" : "style-scope ytd-channel-about-metadata-renderer"})
        for i in soup:
	        channel_all_video_views_i = re.findall('<yt-formatted-string class="style-scope ytd-channel-about-metadata-renderer" no-styles="">.*</yt-formatted-string>', str(i))
	        channel_all_video_views_str = str(channel_all_video_views_i).replace('<yt-formatted-string class="style-scope ytd-channel-about-metadata-renderer" no-styles="">', '').replace('</yt-formatted-string>', '')
	        if "views" in str(channel_all_video_views_str):
	        	channel_all_video_view = re.sub("\\D", "", str(channel_all_video_views_str))
		        self.channel_all_video_views.append(channel_all_video_view)


    def channel_social_links(self):
        soup = self.soup.find_all('a', {"class" : "yt-simple-endpoint container style-scope ytd-c4-tabbed-header-renderer"})
        for i in soup:
	        social_links_i = re.findall('href=".*" title', str(i))
	        if not None in social_links_i:
	        	self.social_link = str(social_links_i).replace('href="', '').replace('" title', '')
	        	if "instagram" in self.social_link:
	        		self.parse_channel_instagram()
	        	elif "twitter" in self.social_link:
	        		self.parse_channel_twitter()
	        	else:
	        		self.parse_channel_blog()


    def parse_channel_instagram(self):
    	self.channel_instagram = []
    	instagram_link = str(self.social_link).replace("['", '').replace("']", '')
    	self.channel_instagram.append(instagram_link)


    def parse_channel_twitter(self):
    	self.channel_twitter = []
    	twitter_link = str(self.social_link).replace("['", '').replace("']", '')
    	self.channel_twitter.append(twitter_link)


    def parse_channel_blog(self):
    	self.channel_blog = []
    	blog_link = str(self.social_link).replace("['", '').replace("']", '')
    	self.channel_blog.append(blog_link)
    	self.channel_link_set()


    def channel_link_set(self):
        self.channel_blog_set = []
        channel_blog_links = self.channel_blog
        channel_blog_link = ''.join(channel_blog_links)
        self.channel_blog_set.append(channel_blog_link)


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
        self.channel_length = []
        countries = self.channel_countries
        countries_join = (''.join(countries))
        p = re.compile('[a-zA-Z]+')
        country = ''.join(p.findall(countries_join))
        if '' is country:
            country = '非表示'
        self.channel_length.append(country)


    def channel_subscriber_set(self):
        self.channel_subscribers_length = []
        subscribers =  self.channel_subscribers
        subscriber = str(list(set(subscribers))).replace("[", '').replace("]", '').replace("'", '')
        self.channel_subscribers_length.append(subscriber)


    def channel_list_csv_scarch_column(self):
        channel_url_i = self.channel_url
        channel_url = channel_url_i.replace('https://www.youtube.com', '').replace('/about', '')
        mask = self.df['channel_url'] == '%s' % channel_url
        self.true_column = self.df[mask]


    def country_subscriber_add_as_csv_file(self):
        try:
            self.true_column['channel_country'] = self.channel_length
        except AttributeError:
            print("エラー")
            print()
            self.true_column['channel_country'] = "エラー"
            pass
        try:
        	self.true_column['channel_subscriber'] = self.channel_subscribers_length
        except AttributeError:
        	print("エラー")
        	print()
        	self.true_column['channel_subscriber'] = "エラー"
        	pass
        try:
        	self.true_column['channel_create_at'] = self.channel_create_at
        except AttributeError:
        	print("エラー")
        	print()
        	self.true_column['channel_create_at'] = "エラー"
        	pass
        try:
        	self.true_column['all_video_views'] = self.channel_all_video_views
        except AttributeError:
        	print("エラー")
        	print()
        	self.true_column['all_video_views'] = "エラー"
        	pass
        try:
        	self.true_column['instagram'] = self.channel_instagram
        except AttributeError:
        	print("エラー")
        	print()
        	self.true_column['instagram'] = "非表示"
        	pass
        try:
        	self.true_column['twitter'] = self.channel_twitter
        except AttributeError:
        	print("エラー")
        	print()
        	self.true_column['twitter'] = "非表示"
        	pass
        try:
        	self.true_column['blog'] = self.channel_blog_set
        except AttributeError:
        	print("エラー")
        	print()
        	self.true_column['blog'] = "非表示"
        	pass
        pd.DataFrame(self.true_column).to_csv(self.channel_list_csv_update_file_path, mode='a', header=False, index=False)
        print("国・登録者をcsvに追記しました")


if __name__ == "__main__":
	scraper = YoutubeChannelInformationScraper()
	scraper.run()
