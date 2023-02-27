import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


def create_plot(data, show_hist=False, plot=True, safeFig = False, n = 10000, name = "Distribution name"):
    """
    Args:
        data: List of datapoints sampled from a distribution
        show_hist: If True create a histogram showing the data given
        plot: If True create a two plots one showing the cummulative mean and with error bars and the distribution mean
        safeFig: If True safe the figure locally. Only works if show_hist or plot is True
        n: Number of sampled from the distribution
        name: Name of the distribution

    Returns: None
    """
    # Data saved as dataframe
    Norm_p = pd.DataFrame(data)

    if show_hist:
        # Create histogram
        plt.hist(data, histtype='step')
        plt.title("Histogram")
        plt.show()

    if plot:
        # Setup for the plots, calculation of key numbers
        Cum_Mean = [Norm_p[0][:i].mean() for i in range(len(data))]
        Cum_std_err = [Norm_p[0][:i].std() / np.sqrt(i) for i in range(1, len(data) + 1)]
        Norm_P_mean = np.mean(Norm_p)
        Norm_P_median = np.median(Norm_p)
        # starts at one as when viewed it makes sense to have the first element be 1
        x_vals = list(range(1, len(Cum_Mean) + 1))

        # Setup for the plots
        fig, axs = plt.subplots(2, figsize = (12,8))
        fig.tight_layout(pad= 3)

        # First value is excluded as standard error of a single point is Nan
        x = np.array(x_vals)[1:]
        ye = np.array(Cum_Mean)[1:]
        yerr = np.array(Cum_std_err[1:len(x) + 1])

        # Creating plot for mean
        axs[0].set_title("Mean for " + name +" distribution")
        axs[0].errorbar(x, ye, yerr=yerr, label='Error bars', linewidth=0.5, ecolor = "blue")
        axs[0].plot(x_vals, Cum_Mean, '-', label = "Cumulative mean", linewidth=3, color = "red")
        axs[0].plot([1, 2, 3, n], [Norm_P_mean, Norm_P_mean, Norm_P_mean, Norm_P_mean], label = "Distribution mean", linewidth=2)
        axs[0].legend(loc = "upper left" ,ncol = 3)

        Cum_Median = Norm_p.rolling(len(Norm_p), min_periods=2).median()
        Cum_Median[0][0] = Norm_p[0][0]
        ye = np.array(Cum_Median)

        # Creating plot for median
        axs[1].set_title("Median for " + name +" distribution")
        axs[1].plot(x_vals, ye, label = "Cumulative median")
        axs[1].plot([0, n], [Norm_P_median, Norm_P_median], label = "Distribution mean")
        axs[1].legend(ncol = 2)

        # Give plots more information
        fig.supxlabel("Number of elements used")
        plt.setp(axs[0], ylabel = "Mean")
        plt.setp(axs[1], ylabel = "Median")

        plt.show()

        if safeFig:
            # Save image of the plot locally
            plt.savefig("my_data/" + name +".png")


# Generate datapoints for each distribution
np.random.seed(10)
n = 10000
normal = np.random.normal(0,4,size=(n))
pareto = np.random.pareto(0.5, size=n)
lognormal = np.random.lognormal(0,4, size= n)

# Sample citation counts from the 2009 computational social science papers
df_papers = pd.read_csv("my_data/df_paper.csv")
mask_2009 = df_papers['year'] == 2009
citationCount_all = np.array(df_papers['citationCount'][mask_2009])
sampledCitationCount = np.random.choice(citationCount_all, n)

# Function call to get the plots
create_plot(normal, n = n, name = "normal")

