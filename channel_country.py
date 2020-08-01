import os
from time import sleep
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
import re
# import time
# import run


class ChannelCountryScraper(object):

    def __init__(self):
        '''
        youtube_url
        '''
        self.youtube_url = "https://www.youtube.com"
        self.user_name = "EGA-CHANNEL1"
        self.channel_about_url = os.path.join(self.youtube_url, 'c', self.user_name, 'about')
        '''
        csv_file_path
        '''
        self.csv_file_name = "./data/youtube_channel_raw_data"
        self.csv_file_path = os.path.join(os.getcwd(), self.csv_file_name+'.csv')
        '''
        extraction_data
        '''
        # self.country = []


    def run(self):
        self.get_page_source()
        self.parse_channel_country()
        # self.channel_country_data_save_as_csv_file()
        self.driver.close()


    def get_page_source(self):
        self.driver = webdriver.Chrome()
        self.driver.get(self.channel_about_url)
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


    def parse_channel_country(self):
        soup = BeautifulSoup(self.current_html, 'html.parser')
        for i in soup.find_all("td", class_="style-scope ytd-channel-about-metadata-renderer"):
            print(i)
            '''
            NoneExclusion
            '''
            # if title is None:
            #     continue
            country = "e"
            # self.country


    def channel_country_data_save_as_csv_file(self):
        data = {
         "country": self.country,
        }
        pd.DataFrame(data).to_csv(self.search_data_csv_file_path,index=False)

if __name__ == "__main__":
    scraper = ChannelCountryScraper()
    scraper.run()
