import os
from time import sleep
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import re
import time
# import run


class YouTubeSearchScraper(object):

    def __init__(self):
        '''
        youtube_url
        '''
        self.search_query = "asmr"
        self.youtube_url = "https://www.youtube.com/"
        self.search_url = "results?search_query="
        '''
        csv_file_path
        '''
        self.search_data_csv_file_name = "./data/youtube_search_raw_data"
        self.channel_list_csv_file_name = "./data/youtube_channel_list"
        self.search_data_csv_file_path = os.path.join(os.getcwd(), self.search_data_csv_file_name+'.csv')
        self.channel_list_csv_file_path = os.path.join(os.getcwd(), self.channel_list_csv_file_name+'.csv')
        self.search_video_url = os.path.join(self.youtube_url, self.search_url, self.search_query)
        '''
        extraction_data
        '''
        self.titles = []
        self.video_urls = []
        self.views = []
        self.channel_urls = []
        self.channel_names = []
        self.video_times = []
        self.create_stamps = []


    def run(self):
        self.get_page_source()
        self.parse_youtube_search_information()
        self.search_data_save_as_csv_file()
        self.channel_list_save_as_csv_file()
        self.driver.close()


    def get_page_source(self):
        self.driver = webdriver.Chrome()
        self.driver.get(self.search_video_url)
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
            sleep(2.5)
            html = self.driver.page_source
            if self.current_html != html:
                self.current_html=html
                t = 0
                start = time.time()
                t = time.time() - start
                t == 20
                break
            # else:
            #     break


    def parse_youtube_search_information(self):
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
            view_i_str_replace_int = [int(s) for s in view_i_str_replace.split() if s.isdigit()]
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
            video_time_i = re.findall('</yt-icon><span aria-label=".* class="style-scope ytd-thumbnail-overlay-time-status-renderer"', str(i))
            video_time_i_str = ",".join(video_time_i)
            video_time = video_time_i_str.replace('</yt-icon><span aria-label="', '').replace('" class="style-scope ytd-thumbnail-overlay-time-status-renderer"', '')
            material = re.findall('id="video-title" title=".*">', str(i))
            '''
            CreateAtOfIntExtractionFunction
            '''
            create_stamp_i = re.findall('<span class="style-scope ytd-video-meta-block">.*前</span>', str(i))
            create_stamp_i_str = ",".join(create_stamp_i)
            create_stamp = create_stamp_i_str.replace('<span class="style-scope ytd-video-meta-block">', '').replace('前</span>', '')
            '''
            NoneExclusion
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
            elif video_time is None:
                continue
            elif video_time is None:
                continue
            if "/watch?v=" in video_url:
                self.titles.append(title)
                self.video_urls.append(video_url)
                self.views.append(view)
                self.channel_urls.append(channel_url)
                self.channel_names.append(channel_name)
                self.video_times.append(video_time)
                self.create_stamps.append(create_stamp)


    def search_data_save_as_csv_file(self):
        data = {
         "title": self.titles,
         "video_url": self.video_urls,
         "view": self.views,
         "channel_url": self.channel_urls,
         "channel_name": self.channel_names,
         "video_time": self.video_times,
         "create_stamp": self.create_stamps
        }
        print(self.channel_names)
        pd.DataFrame(data).to_csv(self.search_data_csv_file_path,index=False)
        # self.driver.close()


    def channel_list_save_as_csv_file(self):
        '''
        Duplicate deletion
        '''
        channel_urls = (list(set(self.channel_urls)))
        channel_names = (list(set(self.channel_names)))
        data = {
         "channel_url": channel_urls,
         "channel_name": channel_names
        }
        pd.DataFrame(data).to_csv(self.channel_list_csv_file_path,index=False)
        


if __name__ == "__main__":
    scraper = YouTubeSearchScraper()
    scraper.run()
