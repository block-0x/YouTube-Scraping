class run(object):

	from search_scraper import YouTubeSearchScraper
	from channel_country_and_subscriber import ChannelCountryAndScraper
	from channel_videos_scraper import YoutubeChannelVideoScraper

	search_scraper = YouTubeSearchScraper()
	search_scraper.run()
	channel_country_and_subscriber__scraper = ChannelCountryAndScraper()
	channel_country_and_subscriber__scraper.run()
	channel_videos_scraper = YoutubeChannelVideoScraper()
	channel_videos_scraper.run()


if __name__ == "__main__":
    ran = run()
    ran.run()
