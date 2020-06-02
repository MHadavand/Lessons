
def BV_Plot_Gridded(Y = None, xlabel = 'Variable 1', ylabel = 'Variable 2'):

	from matplotlib import pyplot as plt
	import matplotlib.gridspec as gridspec
	import PythonTools as PT

	fig = plt.figure(figsize=(10,10), dpi=100, facecolor='w', edgecolor='k')

	wspace=0.02;hspace=0.02; nbins=10; fontsize=25;

	outergrid = gridspec.GridSpec(1,1,wspace=0.05,hspace=0.05,width_ratios=[1],height_ratios=[1])

	g_s = gridspec.GridSpecFromSubplotSpec(2, 2, width_ratios=[4, 1], height_ratios = [1, 4],
	                                      subplot_spec=outergrid[0],wspace=wspace,hspace=hspace)
	ax = plt.subplot(g_s[1, 0])
	PT.bv_plot(x=Y[:,0],y=Y[:,1], ax=ax, cbar = False, stat_xy=(0.2, 0.9))

	ax.grid(True)
	ax.spines['right'].set_visible(False); ax.spines['top'].set_visible(False)
	ax.set_xlabel(xlabel,fontsize=fontsize); ax.set_ylabel(ylabel,fontsize=fontsize);

	axr = plt.subplot(g_s[1, 1], sharey=ax, frameon = False, xlim=(0, 2))
	axr.hist(Y[:,0], color = 'red', orientation = 'horizontal', normed = True, bins=nbins)
	axr.get_xaxis().set_visible(False)
	axr.get_yaxis().set_visible(False)

	axt = plt.subplot(g_s[0, 0], sharex=ax, frameon = False, ylim=(0, 2))
	axt.hist(Y[:,1], color = 'green', normed = True, bins=nbins)
	axt.get_xaxis().set_visible(False)
	axt.get_yaxis().set_visible(False)

	ax.set_xlim([-4,4]); ax.set_ylim([-4,4]);