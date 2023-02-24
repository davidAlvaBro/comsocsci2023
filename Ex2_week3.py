import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

papers_df = pd.read_csv("my_data/df_paper.csv")

mask = papers_df["year"] == 2009.0
papers_2009 = papers_df[mask]
citationCountList = papers_2009["citationCount"].values
print(min(papers_df["year"]))

def plot_loghist(x, bins):
    #Addig 1 to all citationCountList to be able to show it on a log scale
    hist, bins = np.histogram(x+1, bins)
    logbins = np.logspace(0 ,np.log10(bins[-1]),len(bins))
    plt.hist(x+1, bins=logbins)
    plt.xscale('log')
    meanCitations = np.mean(x)
    medianCitations = np.median(x)
    vertLineMean = [meanCitations for bin in logbins]
    vertLineMedian = [medianCitations for bin in logbins]
    plt.plot(logbins, vertLineMedian, label = "Median")
    plt.plot(logbins, vertLineMean, label = "Mean")
    plt.legend()

plot_loghist(citationCountList, 10)

meanCitations = np.mean(papers_2009)

plt.show()

#Meadian er mest brugbar