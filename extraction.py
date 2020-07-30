import os
from time import sleep
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import re


class YoutubeChannelVideoScraper(object):

    def __init__(self):
        self.youtube_url = "https://www.youtube.com"
        self.user_name = "EGA-CHANNEL1"
        self.csv_file_name = "sample"
        self.csv_file_path = os.path.join(os.getcwd(), self.csv_file_name+'.csv')
        self.channel_videos_url = os.path.join(self.youtube_url, 'c', self.user_name, 'videos')
        self.titles = []
        self.video_urls = []
        self.views = []
        self.channel_names = []
        self.channel_subscribers = []
        self.create_ats = []


    def run(self):
        self.get_page_source()
        self.parse_video_title_and_url_and_view()
        # self.parse_channel_name_and_subscriber()
        self.save_as_csv_file()


    def get_page_source(self):
        self.driver = webdriver.Chrome()
        self.driver.get(self.channel_videos_url)
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
            else:
                break


    def parse_video_title_and_url_and_view(self):
        soup = BeautifulSoup(self.current_html, 'html.parser')
        # ChannelNameOfExtractionFunction
        channel_name_i = soup.find("yt-formatted-string", class_="style-scope ytd-channel-name")
        channel_name_lstrip = str(channel_name_i).lstrip('<yt-formatted-string class="style-scope ytd-channel-name" id="text" title="">')
        channel_name_rstrip = channel_name_lstrip.rstrip('</yt-formatted-string>')
        # ChannelSubscriberOfIntExtractionFunction
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
            # print(i)
            # title
            title = (i.get("title"))
            # url
            url = (i.get("href"))
            # view
            view_material_i = (i.get("aria-label"))
            # create_at
            create_at_material_i = (i.get("aria-label"))
            # NoneExclusion
            if title is None:
                continue
            elif url is None:
                continue
            elif view_material_i is None:
                continue
            elif create_at_material_i is None:
                continue
            # ViewOfIntExtractionFunction
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
            # ChannelInfomation
            channel_name = str(channel_name_rstrip)
            channel_subscriber = channel_subscriber_material
            # CreatAtOfIntExtractionFunction
            create_at_material = (i.get("aria-label"))
            create_at_findall = (re.findall('%s .*前' % channel_name, create_at_material))
            create_at_str = ",".join(create_at_findall)
            create_at_replace_x = create_at_str.replace(channel_name, '')
            create_at_replace_x_x = create_at_replace_x.replace(' ', '')
            create_at = create_at_replace_x_x
            # self
            if "/watch?v=" in url:
                self.titles.append(title)
                self.video_urls.append(url)
                self.views.append(view)
                self.channel_names.append(channel_name)
                self.channel_subscribers.append(channel_subscriber)
                self.create_ats.append(create_at)


    def save_as_csv_file(self):
        data = {
         "title": self.titles,
         "url": self.video_urls,
         "view": self.views,
         "channel_name": self.channel_names,
         "channel_subscriber": self.channel_subscribers,
         "create_at": self.create_ats
        }
        pd.DataFrame(data).to_csv(self.csv_file_path,index=False)
        self.driver.close()


if __name__ == "__main__":
    scraper = YoutubeChannelVideoScraper()
    scraper.run()
    