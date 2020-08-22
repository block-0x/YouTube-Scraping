class YoutubeChannelInformationScraper(object):

    def __init__(self):
        self.channel_about_urls = []
        self.channel_subscribers_length = []
        self.channel_length = []
        self.channel_list_csv_file_name = "./../data/channel/youtube_channel_list"
        self.channel_list_csv_file_path = os.path.join(os.getcwd(), self.channel_list_csv_file_name+'.csv')
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
        self.channel_country_subscriber_add_as_csv_file()
        self.drop_channel_list_duplicate()


    def drop_channel_list_duplicate(self):
        df = pd.read_csv(self.channel_list_csv_file_path, engine='python')
        df_drop_duplicate = df.drop_duplicates(subset='channel_url', keep='last')
        pd.DataFrame(df_drop_duplicate).to_csv(self.channel_list_csv_file_path,index=False)
        print(self.channel_list_csv_file_path+"重複削除しました")


    def scrape_at_filter(self):
        df = pd.read_csv(self.channel_list_csv_file_path, engine='python')
        self.df_scrape_at_this_month = df[df['scrape_at'] > dt.datetime(2020,8,13).strftime("%Y/%m/%d")]
        channel_url_data = self.df_scrape_at_this_month.set_index('channel_url')
        channel_urls_ndarray = channel_url_data.index.values
        channel_urls = channel_urls_ndarray.tolist()
        for i in channel_urls:
            youtube_url = 'https://www.youtube.com'
            self.channel_url = ('%s' % i)
            channel_about_url = urlparse.urljoin(youtube_url, self.channel_url+'/about')
            self.channel_about_urls.append(channel_about_url)
            print(self.channel_about_urls[-1])


    '''
    All data update
    '''
    def read_channel_urls(self):
        df = pd.read_csv(self.channel_list_csv_file_path, engine='python')
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
            self.parse_channel_country()
            self.country_set()
            '''
            scraper JapaneWebScraper
            '''
            # self.country_nihongo_true()
            self.channel_subscriber_set()


    def parse_channel_country(self):
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
            if "--" in str(country):
                country = '非表示'
            if "<" in str(country):
                country = '非表示'
            if "[]" in str(country):
                country = '非表示'
            if None is channel_subscriber:
                channel_subscriber = '非表示'
            self.channel_countries.append(country)
            self.channel_subscribers.append(channel_subscriber)


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
        countries = self.channel_countries
        countries_join = (''.join(countries))
        p = re.compile('[a-zA-Z]+')
        country = ''.join(p.findall(countries_join))
        if '' is country:
            country = '非表示'
        self.channel_length.append(country)


    def channel_subscriber_set(self):
        subscribers =  self.channel_subscribers
        subscriber = str(list(set(subscribers))).replace("[", '').replace("]", '').replace("'", '')
        self.channel_subscribers_length.append(subscriber)


    def channel_list_csv_scarch_column(self):
        channel_url_i = self.channel_about_urls
        channel_url = channel_url_i.replace('https://www.youtube.com', '').replace('/about', '')
        mask = self.df['channel_url'] == '%s' % channel_url
        self.true_column = self.df[mask]


    def channel_country_subscriber_add_as_csv_file(self):
        df = self.df_scrape_at_this_month
        print(self.channel_length)
        print(self.channel_subscribers_length)
        df['channel_country'] = self.channel_length
        df['channel_subscriber'] = self.channel_subscribers_length
        pd.DataFrame(df).to_csv(self.channel_list_csv_file_path, mode='a', header=False, index=False)
        print(self.channel_list_csv_file_path+"国・登録者を更新しました")

if __name__ == "__main__":
	scraper = YoutubeChannelInformationScraper()
	scraper.run()
