def summary_stat(main_df, member_id_code, outfl=False):

	import pandas as pd
	import matplotlib.pyplot as plt
	import PythonTools as PT
	from textwrap import wrap

	try:
		assert(isinstance(main_df, pd.DataFrame))
	except:
		raise ValueError('main_df must be a paandas dataframe')


	main_title = main_df['Dimension'][main_df.Member_ID==member_id_code].as_matrix()[0]


	df_member = main_df[['Total', 'Male', 'Female', 'Member_ID']][main_df['Member_ID']==member_id_code]


	male_data=True; female_data=True
	
	if len(df_member[df_member.Male.apply(lambda x: x.isnumeric())])==0:
		male_data=False
		df_member.drop(labels=['Male'],axis=1, inplace=True)

	if len(df_member[df_member.Female.apply(lambda x: x.isnumeric())])==0:
		female_data=False
		df_member.drop(labels=['Female'],axis=1, inplace=True)

	df_member_trim = df_member[df_member.Total.apply(lambda x: x.isnumeric())]
	df_member_trim.reset_index(drop=True, inplace=True)
	df_member_trim = df_member_trim.astype(float)


	fig = plt.figure(figsize=(15,10))

	ax = fig.add_subplot(221)
	_label=("\n".join(wrap(main_title+', Total', 60)))
	PT.pdf_plot(df_member_trim['Total'], bw=-1, ax=ax, line_color='gray', labelfont=14,
				xlabel=_label, barcolor='green', kde_color='black')

	if (male_data):
		ax = fig.add_subplot(222)
		_label=("\n".join(wrap(main_title+', Male', 60)))
		PT.pdf_plot(df_member_trim['Male'], bw=-1, ax=ax, line_color='gray',labelfont=14,
					xlabel=_label, barcolor='blue', kde_color='black')

	if (female_data):
		ax = fig.add_subplot(223)
		_label=("\n".join(wrap(main_title+', Female', 60)))
		PT.pdf_plot(df_member_trim['Female'], bw=-1, ax=ax, line_color='gray',labelfont=14,
					xlabel=_label, barcolor='red', kde_color='black')

	if (all([male_data, female_data])):
		ax = fig.add_subplot(224)
		PT.bv_plot(df_member_trim['Male'],df_member_trim['Female'],bw=-1, ax=ax, 
					   xlabel='Male', label_font_size= 14,
					   ylabel='Female', fontsize=14)

	plt.tight_layout()

	if outfl:

		PT.save_plot(outfl=main_title)
