import pandas as pd
import numpy as np
# import run

class Function(object):

	def run(self):
		self.mean_view()


	def mean_view(self):
		channel_view_data = pd.read_csv('./data/youtube_channel_raw_data.csv',index_col='view')
		views = channel_view_data.index.values
		np.mean(channel_view_data, axis=1)
		view_sum = sum(views)
		view_number = len(views)
		view_mean = view_sum / view_number
		print(round(view_mean))


if __name__ == "__main__":
    mean_view = Function()
    mean_view.run()
