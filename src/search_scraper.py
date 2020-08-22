import os
from time import sleep
import pandas
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import re
import time
import datetime
import datetime as dt
try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse


class YouTubeSearchScraper(object):

    def __init__(self):
        '''
        csv_file_path
        '''
        self.search_data_csv_file_name = "./../data/search/youtube_search_csv_data"
        self.channel_list_csv_file_name = "./../data/channel/youtube_channel_list"
        self.search_csv_data_file_path = os.path.join(os.getcwd(), self.search_data_csv_file_name+'.csv')
        self.channel_list_csv_file_path = os.path.join(os.getcwd(), self.channel_list_csv_file_name+'.csv')
        '''
        extraction_data
        '''
        self.search_urls = []
        '''
        scrape_at_stmp
        '''
        self.scrape_at = datetime.date.today().strftime("%Y/%m/%d")


    def run(self):
        self.read_search_query()
        self.get_page_source()
        self.csv_file_drop_duplicate()
        self.driver.close()


    def read_search_query(self):
        search_query_csv = pd.read_csv('./../data/search/search_list.csv',index_col='search_query')
        search_query_values = search_query_csv.index.values
        search_queries = search_query_values.tolist()
        for i in search_queries:
            youtube_url = 'https://www.youtube.com'
            self.youtube_search_url = 'results?search_query='
            self.search_query = ('%s' % i)
            search_url = urlparse.urljoin(youtube_url, 'results?search_query='+self.search_query)
            self.search_urls.append(search_url)


    def get_page_source(self):
        self.driver = webdriver.Firefox()
        for self.query_item in self.search_urls:
            self.driver.get(self.query_item)
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
                sleep(2.3)
                html = self.driver.page_source
                if self.current_html != html:
                    self.current_html=html
                    # t = 0
                    # start = time.time()
                    # t = time.time() - start
                    # t == 10
                    # self.parse_search_videos()
                    # self.search_data_save_as_csv_file()
                    # self.channel_list_add_as_csv_file()
                    # break
                else:
                    self.parse_search_videos()
                    self.search_data_save_as_csv_file()
                    self.channel_list_add_as_csv_file()
                    break


    def parse_search_videos(self):
        self.turn_ids = []
        self.titles = []
        self.video_urls = []
        self.views = []
        self.channel_urls = []
        self.channel_names = []
        self.video_lengths = []
        self.create_stamps = []
        self.queries = []
        self.scrape_ats = []
        self.channel_countries = []
        self.channel_subscribers = []
        self.mean_views = []
        self.create_ats = []
        self.tags = []
        self.descriptions = []
        self.likes = []
        self.dislikes = []
        self.channel_create_ats = []
        self.all_video_views = []
        self.instagrams = []
        self.twitters = []
        self.blogs = []
        turn_id = 0
        soup = BeautifulSoup(self.current_html, 'html.parser')
        for i in soup.find_all("div", id = "dismissable"):
            '''
            TitleOfIntExtractionFunction
            '''
            title_i = re.findall('id="video-title" title=".*">', str(i))
            title_i_str = ",".join(title_i)
            title = title_i_str.replace('id="video-title" title="', '').replace('">', '').replace('&amp;', '&')
            '''
            UrlOfIntExtractionFunction
            '''
            video_url_i = re.findall('class="yt-simple-endpoint style-scope ytd-video-renderer".* id="video-title"', str(i))
            video_url_i_str = ",".join(video_url_i)
            video_url = video_url_i_str.replace('class="yt-simple-endpoint style-scope ytd-video-renderer" href=', '').replace(' id="video-title"', '').strip('""')
            '''
            ViewOfIntExtractionFunction
            '''
            view_i = re.findall('<yt-formatted-string aria-label=".* 回視聴" class="style-scope ytd-video-renderer">', str(i))
            view_i_str = ",".join(view_i)
            view_i_str_replace = view_i_str.replace('<yt-formatted-string aria-label="', '').replace('前 ', '').replace(' 回視聴" class="style-scope ytd-video-renderer">', '').replace(',', '')
            try:
                view_i_str_replace_int = [int(s) for s in view_i_str_replace.split() if s.isdigit()]
            except ValueError:
                continue
            if view_i_str_replace_int:
                view = (view_i_str_replace_int[-1])
            else:
                continue
            '''
            ChannelUrlNameOfIntExtractionFunction
            '''
            channel_url_i = re.findall('<a aria-label="チャンネルに移動" class="style-scope ytd-video-renderer" href=".*">', str(i))
            channel_url_i_str = ",".join(channel_url_i)
            channel_url = channel_url_i_str.replace('<a aria-label="チャンネルに移動" class="style-scope ytd-video-renderer" href="', '').replace('">', '').strip('""')
            '''
            ChannelNameOfIntExtractionFunction
            '''
            channel_name_i = re.findall('<yt-formatted-string class="style-scope ytd-channel-name" has-link-only_="" id="text" title=""><a class="yt-simple-endpoint style-scope yt-formatted-string" dir="auto" href=".*</a></yt-formatted-string>', str(i))
            channel_name_i_str = ",".join(channel_name_i)
            channel_name = channel_name_i_str.replace('<yt-formatted-string class="style-scope ytd-channel-name" has-link-only_="" id="text" title=""><a class="yt-simple-endpoint style-scope yt-formatted-string" dir="auto" href="', '').replace('</a></yt-formatted-string>', '').replace('%s' % channel_url, '').replace('" spellcheck="false">', '')
            material = re.findall('id="video-title" title=".*">', str(i))
            '''
            VideoTimeOfIntExtractionFunction
            '''
            video_length_i = re.findall('</yt-icon><span aria-label=".* class="style-scope ytd-thumbnail-overlay-time-status-renderer"', str(i))
            video_length_i_str = ",".join(video_length_i)
            video_length = video_length_i_str.replace('</yt-icon><span aria-label="', '').replace('" class="style-scope ytd-thumbnail-overlay-time-status-renderer"', '')
            material = re.findall('id="video-title" title=".*">', str(i))
            '''
            CreateAtOfIntExtractionFunction
            '''
            create_stamp_i = re.findall('<span class="style-scope ytd-video-meta-block">.*前</span>', str(i))
            create_stamp_i_str = ",".join(create_stamp_i)
            create_stamp = create_stamp_i_str.replace('<span class="style-scope ytd-video-meta-block">', '').replace('前</span>', '')
            '''
            Validation
            '''
            if title is None:
                continue
            elif video_url is None:
                continue
            elif view is None:
                continue
            elif channel_url is None:
                continue
            elif channel_name is None:
                continue
            elif video_length is None:
                continue
            elif video_length is None:
                continue
            elif "," in channel_url:
                continue
            turn_id += 1
            queriy_material = self.query_item
            queriy = queriy_material.replace('https://www.youtube.com/results?search_query=', '')
            scrape_at = self.scrape_at
            channel_country = None
            channel_subscriber = None
            mean_view = None
            create_at = None
            tag = None
            description = None
            like = None
            dislike = None
            channel_create_at = None
            all_video_view = None
            instagram = None
            twitter = None
            blog = None
            if "/watch?v=" in video_url:
                self.turn_ids.append(turn_id)
                self.titles.append(title)
                self.video_urls.append(video_url)
                self.views.append(view)
                self.channel_urls.append(channel_url)
                self.channel_names.append(channel_name)
                self.video_lengths.append(video_length)
                self.create_stamps.append(create_stamp)
                self.queries.append(queriy)
                self.scrape_ats.append(scrape_at)
                self.channel_countries.append(channel_country)
                self.channel_subscribers.append(channel_subscriber)
                self.mean_views.append(mean_view)
                self.create_ats.append(create_at)
                self.tags.append(tag)
                self.descriptions.append(description)
                self.likes.append(like)
                self.dislikes.append(dislike)
                self.channel_create_ats.append(channel_create_at)
                self.all_video_views.append(all_video_view)
                self.instagrams.append(instagram)
                self.twitters.append(twitter)
                self.blogs.append(blog)


    def search_data_save_as_csv_file(self):
        data = {
         "turn_id": self.turn_ids,
         "title": self.titles,
         "video_url": self.video_urls,
         "view": self.views,
         "channel_url": self.channel_urls,
         "channel_name": self.channel_names,
         "video_length": self.video_lengths,
         "create_stamp": self.create_stamps,
         "queriy": self.queries,
         "scrape_at": self.scrape_ats,
         "channel_country": self.channel_countries,
         "channel_subscriber": self.channel_subscribers,
         "mean_view": self.mean_views,
         "create_at": self.create_ats,
         "tag": self.tags,
         "description": self.descriptions,
         "like": self.likes,
         "dislike": self.dislikes
        }
        if 0 is os.path.getsize(self.search_csv_data_file_path):
            pd.DataFrame(data).to_csv(self.search_csv_data_file_path,index=False)
            print(self.search_csv_data_file_path+"新規入力")
        else:
            try:
                pd.DataFrame(data).to_csv(self.search_csv_data_file_path, mode='a', header=False, index=False)
                print(self.search_csv_data_file_path+"に追記")
            except ValueError:
                print(len(self.turn_ids))
                print(len(self.titles))
                print(len(self.video_urls))
                print(len(self.views))
                print(len(self.channel_urls))
                print(len(self.video_lengths))
                print(len(self.create_stamps))
                print(len(self.queries))
                print(len(self.scrape_ats))


    def channel_list_add_as_csv_file(self):
        data = {
         "channel_url": self.channel_urls,
         "channel_name": self.channel_names,
         "scrape_at": self.scrape_ats,
         "channel_country": self.channel_countries,
         "channel_subscriber": self.channel_subscribers,
         "mean_view": self.mean_views,
         "channel_create_at": self.channel_create_ats,
         "all_video_views": self.all_video_views,
         "instagram": self.instagrams,
         "twitter": self.twitters,
         "blog": self.blogs
        }
        if 0 is os.path.getsize(self.channel_list_csv_file_path):
            try:
                pd.DataFrame(data).to_csv(self.channel_list_csv_file_path,index=False)
                print(self.channel_list_csv_file_path+"新規入力")
            except ValueError:
                print(len(self.channel_urls))
                print(len(self.channel_names))
                print(len(self.scrape_ats))
                print(len(self.channel_countries))
                print(len(self.channel_subscribers))
                print(len(self.mean_views))
                print(len(self.channel_create_ats))
                print(len(self.all_video_views))
                print(len(self.instagrams))
                print(len(self.twitters))
                print(len(self.blogs))
        else:
            pd.DataFrame(data).to_csv(self.channel_list_csv_file_path, mode='a', header=False, index=False)
            print(self.channel_list_csv_file_path+"に追記")


    def csv_file_duplicate_count(self):
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


    # def csv_file_duplicate_count(self):
    #     df = pd.read_csv(self.channel_list_csv_file_path)
    #     df.loc[self.scrape_at]
    #     self.df_scrape_at_filter = df[df.duplicated(subset='video_url', keep=False, inplace=True)]
    #     print(self.df_scrape_at_filter)
    #     channel_url_data = self.df_scrape_at_filter.set_index('video_url')
    #     df.replace({'age': {24: 100, 18: 0}, 'point': {None: カウントした}})
    #     channel_urls_ndarray = channel_url_data.index.values
    #     channel_urls = channel_urls_ndarray.tolist()
    #     for i in channel_urls:
    #         youtube_url = 'https://www.youtube.com'
    #         self.channel_url = ('%s' % i)
    #         channel_about_url = urlparse.urljoin(youtube_url, self.channel_url+'/about')
    #         self.channel_about_urls.append(channel_about_url)


    def csv_file_drop_duplicate(self):
        df = pd.read_csv('./../data/channel/youtube_channel_list.csv')
        df_drop_duplicate = df.drop_duplicates(subset='channel_url')
        pd.DataFrame(df_drop_duplicate).to_csv(self.channel_list_csv_file_path,index=False)
        print(self.channel_list_csv_file_path+"重複削除しました")


class SearchQuery(object):

    def __init__(self):
        self.channel_country = []
        self.channel_subscriber = []
        self.mean_views = []
        '''
        csv_file_path
        '''
        self.search_data_csv_file_name = "./../data/search/youtube_search_csv_data"
        self.channel_list_csv_file_name = "./../data/channel/youtube_channel_list"
        self.search_csv_data_file_path = os.path.join(os.getcwd(), self.search_data_csv_file_name+'.csv')
        self.channel_list_csv_file_path = os.path.join(os.getcwd(), self.channel_list_csv_file_name+'.csv')
        '''
        extraction_data
        '''
        self.search_urls = []
        '''
        scrape_at_stmp
        '''
        self.dt_now = datetime.datetime.now()
        self.dt_year = self.dt_now.year
        self.dt_month = self.dt_now.month
        self.dt_day = self.dt_now.day


    def run(self):
        self.drop_channel_list_duplicate()
        self.read_csv_file()
        self.channel_list_csv_scarch_column()


    def drop_channel_list_duplicate(self):
        df = pd.read_csv(self.channel_list_csv_file_path)
        df_drop_duplicate = df.drop_duplicates(subset='channel_url', keep='last')
        pd.DataFrame(df_drop_duplicate).to_csv(self.channel_list_csv_file_path,index=False)
        print(self.channel_list_csv_file_path+"重複削除しました")


    def read_csv_file(self):
        self.channel_list_df = pd.read_csv(self.channel_list_csv_file_path)
        channel_list_df_channel_url_data = self.channel_list_df.set_index('channel_url')
        channel_list_channel_urls_ndarray = channel_list_df_channel_url_data.index.values
        search_df = pd.read_csv(self.search_csv_data_file_path)
        df_scrape_at_this_today = search_df[search_df['scrape_at'] == dt.datetime(int(self.dt_year),int(self.dt_month),int(self.dt_day)).strftime("%Y/%m/%d")]
        search_channel_url_data = df_scrape_at_this_today.set_index('channel_url')
        self.search_channel_urls_ndarray = search_channel_url_data.index.values


    def channel_list_csv_scarch_column(self):
        for i in self.search_channel_urls_ndarray:
            mask = self.channel_list_df['channel_url'] == '%s' % i
            true_column = self.channel_list_df[mask]
            channel_country = true_column['channel_country']
            channel_subscriber = true_column['channel_subscriber']
            mean_view = true_column['mean_view']
            self.channel_country.append(channel_country)
            self.channel_subscriber.append(channel_subscriber)
            self.mean_views.append(mean_view)


if __name__ == "__main__":
    scraper = YouTubeSearchScraper()
    scraper.run()
    # query = SearchQuery()
    # query.run()
