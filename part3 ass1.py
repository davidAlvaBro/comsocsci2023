import numpy as np
import matplotlib.pyplot as plt
import pandas as pd


def create_plot(data, mean, median, show_hist=False, plot=True, safeFig = False, n = 10000, name = "Distribution name"):
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
        
        # starts at one as when viewed it makes sense to have the first element be 1
        x_vals = list(range(1, len(Cum_Mean) + 1))

        # Setup for the plots
        fig, axs = plt.subplots(2, figsize = (12,8))
        fig.tight_layout(pad= 3)

        # First value is excluded as standard error of a single point is Nan
        ye = np.array(Cum_Mean)[1:]
        yerr = np.array(Cum_std_err[1:])

        # Creating plot for mean
        axs[0].set_title("Mean for " + name +" distribution")
        axs[0].errorbar(x_vals[1:], ye, yerr=yerr, label='Error bars', linewidth=0.5, ecolor = "blue", fmt='none')
        axs[0].plot(x_vals, Cum_Mean, '-', label = "Cumulative mean", linewidth=1, color = "red")
        axs[0].plot([1, n], [mean, mean], label = "Distribution mean", linewidth=2, color="orange")
        axs[0].legend(loc = "upper left", ncol = 3)

        Cum_Median = Norm_p.rolling(len(Norm_p), min_periods=2).median()
        Cum_Median[0][0] = Norm_p[0][0]
        ye = np.array(Cum_Median)

        # Creating plot for median
        axs[1].set_title("Median for " + name +" distribution")
        axs[1].plot(x_vals, ye, label = "Cumulative median")
        axs[1].plot([0, n], [median, median], label = "Distribution mean")
        axs[1].legend(ncol = 2)

        # Give plots more information
        fig.supxlabel("Number of elements used")
        plt.setp(axs[0], ylabel = "Mean")
        plt.setp(axs[1], ylabel = "Median")

        plt.show()

        if safeFig:
            # Save image of the plot locally
            plt.savefig("my_data/" + name +".png")

# Generate distributions 
np.random.seed(10)
n = 10000
n2 = 500

# Normal distribution 
normal_mu = 0 
normal_std = 4
normal = np.random.normal(normal_mu, normal_std, size=(n))

# pareto 
pareto_alpha = 0.5 
pareto = np.random.pareto(pareto_alpha, size=n)
pareto_mean = None 
pareto_median = 1*(2)**(1/pareto_alpha)

# lognormal 
lognormal_mu = 0 
lognormal_std = 4
lognormal = np.random.lognormal(lognormal_mu, lognormal_std, size= n)
lognormal_mean = np.exp(lognormal_mu + lognormal_std**2 / 2)
lognormal_median = np.exp(lognormal_mu)


# Plot normal
create_plot(normal, mean=normal_mu, median=normal_mu, n=n, name="normal")
create_plot(normal[:n2], mean=normal_mu, median=normal_mu, n=n2, name="normal (500)")

# Pareto 
create_plot(pareto, mean=pareto_mean, median=pareto_median, n=n, name="pareto")
create_plot(pareto[:n2], mean=pareto_mean, median=pareto_median, n=n2, name="pareto (500)")

# Pareto
create_plot(lognormal, mean=lognormal_mean, median=lognormal_median, n=n, name="lognormal")
create_plot(lognormal[:n2], mean=lognormal_mean, median=lognormal_median, n=n2, name="logmormal (500)")


# Sample citation counts from the 2009 computational social science papers
df_papers = pd.read_csv("DataFoundPreviously/df_paper.csv")
mask_2009 = df_papers['year'] == 2009
citationCount_all = np.array(df_papers['citationCount'][mask_2009])
citations_mean = np.mean(citationCount_all)
citations_median = np.median(citationCount_all)
sampledCitationCount = np.random.choice(citationCount_all, n)

create_plot(sampledCitationCount, mean=citations_mean, median=citations_median, n=n, name="citations")
create_plot(sampledCitationCount[:n2], mean=citations_mean, median=citations_median, n=n2, name="citations (500)")

