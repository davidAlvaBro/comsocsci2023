import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


def name(data, show_hist=False, plot=True, safeFig = False, n = 10000, name = "Distribution name"):
    Norm_p = pd.DataFrame(data)

    if show_hist:
        plt.hist(data, histtype='step')  # arguments are passed to np.histogram
        plt.title("Histogram")
        plt.show()

    if plot:
        Cum_Mean = [Norm_p[0][:i].mean() for i in range(len(data))]
        Cum_std_err = [Norm_p[0][:i].std() / np.sqrt(i) for i in range(1, len(data) + 1)]
        Norm_P_mean = np.mean(Norm_p)
        Norm_P_median = np.median(Norm_p)
        x_vals = list(range(1, len(Cum_Mean) + 1))

        fig, axs = plt.subplots(2)
        fig.tight_layout(pad= 3)
        x = np.array(x_vals)[1:]
        ye = np.array(Cum_Mean)[1:]  # First value is excluded as standard error of a single point is Nan
        yerr = np.array(Cum_std_err[1:len(x) + 1])


        axs[0].set_title("Mean for " + name +" distribution")

        axs[0].errorbar(x, ye, yerr=yerr, label='Error bars', linewidth=0.5, ecolor = "blue")
        axs[0].plot(x_vals, Cum_Mean, '-', label = "Cumulative mean")
        axs[0].plot([1, 2, 3, n], [Norm_P_mean, Norm_P_mean, Norm_P_mean, Norm_P_mean], label = "Distribution mean")
        axs[0].legend(ncol = 3)
        #plt.show()

        Cum_Median = Norm_p.rolling(len(Norm_p), min_periods=2).median()
        Cum_Median[0][0] = Norm_p[0][0]

        ye = np.array(Cum_Median)
        axs[1].set_title("Median for " + name +" distribution")

        axs[1].plot(x_vals, ye, label = "Cumulative median")

        # plt.legend(loc='lower right')
        axs[1].plot([0, n], [Norm_P_median, Norm_P_median], label = "Distribution mean")
        axs[1].legend(ncol = 2)

        fig.supxlabel("Number of elements used")

        plt.setp(axs[0], ylabel = "Mean")
        plt.setp(axs[1], ylabel = "Median")


        plt.show()
        if safeFig:
            plt.savefig("my_data/" + name +".png")


np.random.seed(10)
n = 10000
normal = np.random.normal(0,4,size=(n))
pareto = np.random.pareto(0.5, size=n)
lognormal = np.random.lognormal(0,4, size= n)
df_papers = pd.read_csv("my_data/df_paper.csv")
citationCount = df_papers['citationCount']
sampledCitationCount = np.random.choice(np.array(citationCount), n)

name(sampledCitationCount, safeFig=False, n = n, name = "sampledCitationCount")

