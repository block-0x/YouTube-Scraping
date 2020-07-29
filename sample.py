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
        self.user_name = "youtube_chanel_name"
        self.csv_file_name = "sample"
        self.csv_file_path = os.path.join(os.getcwd(), self.csv_file_name+'.csv')
        self.channel_videos_url = os.path.join(self.youtube_url, 'user_or_c_or_chanel', self.user_name, 'videos')
        self.titles = []
        self.video_urls = []
        self.views = []

    def run(self):
        self.get_page_source()
        self.parse_video_title_and_url()
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
            sleep(3)
            html = self.driver.page_source
            if self.current_html != html:
                self.current_html=html
            else:
                break

    def parse_video_title_and_url(self):
        soup = BeautifulSoup(self.current_html, 'html.parser')
        for i in soup.find_all("a"):
            title = (i.get("title"))
            url = (i.get("href"))
            view_material_text = (i.get("aria-label"))
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
                print(view)
            if "/watch?v=" in url:
                self.titles.append(title)
                self.video_urls.append(url)
                self.views.append(view)

    def save_as_csv_file(self):
        data = {
         "title": self.titles,
         "url": self.video_urls,
         "view": self.views
        }
        pd.DataFrame(data).to_csv(self.csv_file_path,index=False)


if __name__ == "__main__":
    scraper = YoutubeChannelVideoScraper(user_name="HikakinTV", csv_file_name="HikakinTV")
    scraper.run()