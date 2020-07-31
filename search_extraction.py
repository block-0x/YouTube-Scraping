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
        self.youtube_url = "https://www.youtube.com/"
        self.search_url = "results?search_query="
        self.search_query = "asmr mukbang"
        self.csv_file_name = "./data/youtube_search_raw_data"
        self.csv_file_path = os.path.join(os.getcwd(), self.csv_file_name+'.csv')
        self.search_video_url = os.path.join(self.youtube_url, self.search_url, self.search_query)
        self.titles = []
        self.video_urls = []
        self.views = []
        self.channel_names = []
        # self.channel_subscribers = []
        # self.create_ats = []


    def run(self):
        self.get_page_source()
        self.parse_video_title_and_url_and_view()
        self.save_as_csv_file()


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
            sleep(2)
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


    def parse_video_title_and_url_and_view(self):
        soup = BeautifulSoup(self.current_html, 'html.parser')
        # channel_name = soup.find_all("a", class_="yt-simple-endpoint style-scope yt-formatted-string")
        # print(channel_name)
        for i in soup.find_all("div", id = "dismissable"):
            # print(i)
            # TitleOfIntExtractionFunction
            title_i = re.findall('id="video-title" title=".*">', str(i))
            title_i_str = ",".join(title_i)
            title = title_i_str.replace('id="video-title" title="', '').replace('">', '').replace('&amp;', '&')
            # UrlOfIntExtractionFunction
            url_i = re.findall('class="yt-simple-endpoint style-scope ytd-video-renderer".* id="video-title"', str(i))
            url_i_str = ",".join(url_i)
            url = url_i_str.replace('class="yt-simple-endpoint style-scope ytd-video-renderer" href=', '').replace(' id="video-title"', '')
            # material
            url = (i.get("aria-label"))
            material = (i.get("aria-label"))
            # create_at
            # create_at_material_i = (i.get("aria-label"))
            # NoneExclusion
            if title is None:
                continue
            elif url is None:
                continue
            elif material is None:
                continue
            # MaterialOfIntExtractionFunction
            material = material.replace('　', '')
            # print(channel_name_material_x)
            # viewOfIntExtractionFunction
            view_material = material
            view_findall = (re.findall('前 .*回視聴', view_material))
            if view_findall:
                view_str = ",".join(view_findall)
                view_replace = view_str.replace('前 ', '').replace(' 回視聴', '').replace(',', '')
                view_int = [int(s) for s in view_replace.split() if s.isdigit()]
                view_last_int = (view_int[-1])
                view = view_last_int
            # channel_name_material
            # channel_name_ = i
            # channel_name_material = re.findall('<a class="yt-simple-endpoint style-scope yt-formatted-string".*</a>', str(i))
            # print(str(i))
            # channel_name_
            # ChannelNameInfomation
            # material = material_i.replace('　', '')
            # channel_name_material = material
            # channel_name_findall = (re.findall('作成者: .*前 ', channel_name_material))
            # if channel_name_findall:
            #     channel_name_str = ",".join(channel_name_findall)
            #     channel_name_replace = channel_name_str.replace('作成者:', '').replace(' ', '').replace(',', '')
                # print(channel_name_replace)
                # channel_name_int = [int(s) for s in channel_name_replace.split() if s.isdigit()]
                # channel_name_last_int = (channel_name_int[-1])
                # print(channel_name_last_int)
            channel_name = "channel_name_last_int"
            # channel_subscriber = channel_subscriber_material
            # CreatAtOfIntExtractionFunction
            # create_at_material = (i.get("aria-label"))
            # create_at_findall = (re.findall('%s .*前' % channel_name, create_at_material))
            # create_at_str = ",".join(create_at_findall)
            # create_at_replace_x = create_at_str.replace(channel_name, '')
            # create_at_replace_x_x = create_at_replace_x.replace(' ', '')
            # create_at = create_at_replace_x_x
            # self
            if "/watch?v=" in url:
                self.titles.append(title)
                self.video_urls.append(url)
                self.views.append(view)
                self.channel_names.append(channel_name)
                # self.channel_subscribers.append(channel_subscriber)
                # self.create_ats.append(create_at)
                # print(self.create_ats.append(create_at))


    def save_as_csv_file(self):
        data = {
         "title": self.titles,
         "url": self.video_urls,
         "view": self.views,
         "channel_name": self.channel_names,
         # "channel_subscriber": self.channel_subscribers,
         # "create_at": self.create_ats
        }
        pd.DataFrame(data).to_csv(self.csv_file_path,index=False)
        self.driver.close()


if __name__ == "__main__":
    scraper = YouTubeSearchScraper()
    scraper.run()
