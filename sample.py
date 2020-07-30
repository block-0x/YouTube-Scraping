import os
from time import sleep
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import re


class YoutubeChannelVideoScraper(object):

    def __init__(self, user_name, csv_file_name):
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


    def run(self):
        self.get_page_source()
        self.parse_video_title_and_url_and_view()
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
            sleep(2.5)
            html = self.driver.page_source
            if self.current_html != html:
                self.current_html=html
            else:
                break


    def parse_video_title_and_url_and_view(self):
        soup = BeautifulSoup(self.current_html, 'html.parser')
        channel_name_i = soup.find("yt-formatted-string", class_="style-scope ytd-channel-name")
        channel_name_lstrip = str(channel_name_i).lstrip('<yt-formatted-string class="style-scope ytd-channel-name" id="text" title="">')
        channel_name_rstrip = channel_name_lstrip.rstrip('</yt-formatted-string>')
        # print(channel_name_rstrip)
        channel_subscriber_i = soup.find("yt-formatted-string", class_="style-scope ytd-c4-tabbed-header-renderer")
        # print(channel_subscriber_i)
        # channel_subscriber_str = str(channel_subscriber_i)
        # print(channel_subscriber_str)
        # channel_subscriber_replace = channel_subscriber_str.replace('　', ' ')
        # print(channel_subscriber_replace)
        channel_subscriber_lstrip = str(channel_subscriber_i).lstrip('<yt-formatted-string class="style-scope ytd-c4-tabbed-header-renderer" id="subscriber-count">')
        # print(channel_subscriber_lstrip)
        channel_subscriber_rstrip = channel_subscriber_lstrip.rstrip('</yt-formatted-string>')
        # print(channel_subscriber_rstrip)
        if "万" in channel_subscriber_rstrip:
            print("万人以上")
            channel_subscriber_replace = channel_subscriber_rstrip.replace(' ', '')
            print(channel_subscriber_replace)
            channel_subscriber_sub = re.sub("\\D", "", str(channel_subscriber_replace))
            print(channel_subscriber_sub)
            channel_subscriber_add_million = channel_subscriber_sub + '0000'
            print(channel_subscriber_add_million)
            channel_subscriber_material = int(channel_subscriber_add_million)
        else:
            print("万人以下")
            channel_subscriber_replace = channel_subscriber_rstrip.replace(' ', '')
            # print(channel_subscriber_replace)
            channel_subscriber_sub = re.sub("\\D", "", str(channel_subscriber_replace))
            channel_subscriber_material = int(channel_subscriber_sub)
            # channel_subscriber_material = [int(s) for s in channel_subscriber_replace.split() if s.isdigit()]
        for i in soup.find_all("a"):
            title = (i.get("title"))
            url = (i.get("href"))
            view_material_text = (i.get("aria-label"))
            channel_name = channel_name_rstrip
            channel_subscriber = channel_subscriber_material
            if title is None:
                continue
            elif url is None:
                continue
            elif view_material_text is None:
                continue
            view_material = view_material_text.replace('　', ' ')
            view_text = (re.findall('前 .*回視聴', view_material))
            if view_text:
                string = ",".join(view_text)
                string_new = string.replace('前 ', '')
                view_text_x = string_new.replace(' 回視聴', '')
                view_text_y = view_text_x.replace(',', '')
                str_list_new_x = [int(s) for s in view_text_y.split() if s.isdigit()]
                view = (str_list_new_x[-1])
            if "/watch?v=" in url:
                self.titles.append(title)
                self.video_urls.append(url)
                self.views.append(view)
                self.channel_names.append(channel_name)
                self.channel_subscribers.append(channel_subscriber)
                
    def save_as_csv_file(self):
        data = {
         "title": self.titles,
         "url": self.video_urls,
         "view": self.views,
         "channel_name": self.channel_names,
         "channel_subscriber": self.channel_subscribers
        }
        pd.DataFrame(data).to_csv(self.csv_file_path,index=False)


if __name__ == "__main__":
    scraper = YoutubeChannelVideoScraper(user_name="EGA-CHANNEL1", csv_file_name="EGA-CHANNEL1")
    scraper.run()