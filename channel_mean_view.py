import pandas as pd
import numpy as np
# import run

class Function(object):

	def run(self):
		self.mean_view()


	def mean_view(self):
		df = pd.read_csv('./data/youtube_raw_data.csv',index_col='view')
		views = df.index.values
		np.mean(df, axis=1)
		s = sum(views)
		N = len(views)
		mean = s / N
		print('平均:{0:.2f}'.format(mean))
