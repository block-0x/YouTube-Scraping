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
        self.user_name = "HikakinTV"
        self.csv_file_name = "sample"
        self.csv_file_path = os.path.join(os.getcwd(), self.csv_file_name+'.csv')
        self.channel_videos_url = os.path.join(self.youtube_url, 'user', self.user_name, 'videos')
        self.titles = []
        self.video_urls = []
        self.views = []

    def run(self):
        #ソースの取得
        self.get_page_source()
        #動画とURLの抽出
        self.parse_video_title_and_url()
        #データの保存
        self.save_as_csv_file()

    def get_page_source(self):
        '''
        YoutubeChannelページの
        最下部までスクロールしたページソースを取得
        '''
        # ブラウザ操作の準備
        self.driver = webdriver.Chrome()
        self.driver.get(self.channel_videos_url)
        self.current_html = self.driver.page_source

        # 動画一覧要素へ移動
        element = self.driver.find_element_by_xpath('//*[@class="style-scope ytd-page-manager"]')
        actions = ActionChains(self.driver)
        actions.move_to_element(element)
        actions.perform()
        actions.reset_actions()

        # 最下部までスクロールしたソースを取得
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
        '''
        タイトルと動画URLを抽出
        '''
        soup = BeautifulSoup(self.current_html, 'html.parser')
        for i in soup.find_all("a"):
            title = (i.get("title"))
            url = (i.get("href"))
            # 再生回数の材料
            view_material_text = (i.get("aria-label"))
            if title is None:
                continue
            elif url is None:
                continue
            elif view_material_text is None:
                continue
            # 再生回数の材料の空白を削除
            view_material = view_material_text.replace('　', ' ')
            # 文字列中の前から回視聴以外を削除
            view_text = (re.findall('前 .*回視聴', view_material))
            if view_text:
                # if view_text in ' 秒 ':
                # view_text = (re.findall('前 .*回視聴', view_material))
                string = ",".join(view_text)
                string_new = string.replace('前 ', '')
                view_text_x = string_new.replace(' 回視聴', '')
                view_text_y = view_text_x.replace(',', '')
                # view_text_z = view_text_y.replace(' ', '')
                # str_list_new = view_text_y.split(",")
                # print(str_list_new)
                str_list_new_x = [int(s) for s in view_text_y.split() if s.isdigit()]
                view = (str_list_new_x[-1])
                print(view)
                # view_text_x.isupper()
                # view_text.replace('前 ', '')
                # str_list_new.replace('', '')
            # print(view_text)
            # もし、文字列中に秒があった場合
            # if view_text in ' 秒 ':
            # False not in [view_material in ' 秒 ' for view_material in ['秒']]
            # if '秒' in view_text:
            # 文字列中の秒から回視聴以外を削除
            # view_text = (re.findall('秒 .*回視聴', view_material))
            # 数字以外を削除
            # view_text = str(view_text)
            # view = (re.sub("\\D", "", view_text))
            if "/watch?v=" in url:
                self.titles.append(title)
                self.video_urls.append(url)
                self.views.append(view)

    def save_as_csv_file(self):
        '''
        CSVファイルとして保存
        '''
        data = {
         "title": self.titles,
         "url": self.video_urls,
         "view": self.views
        }
        pd.DataFrame(data).to_csv(self.csv_file_path,index=False)


if __name__ == "__main__":
    scraper = YoutubeChannelVideoScraper(user_name="HikakinTV", csv_file_name="HikakinTV")
    scraper.run()