import numpy as np
import pandas as pd
from scipy.stats import pearsonr
from scipy import stats
import matplotlib.pyplot as plt



data = pd.read_csv("/comsocsci2023/my_data/Data_1_2_3_4.txt", sep="\t", header=None)
data_numpy = data.to_numpy()
data_floats = np.zeros_like(data_numpy)

for i,list1 in enumerate(data_numpy):
    for j,num in enumerate(list1):
        if num != "None":
            data_floats[i,j] = float(num)


#mean
mean1_xy = np.mean(data_floats[:11], 0)
mean2_xy = np.mean(data_floats[12:23], 0)
mean3_xy = np.mean(data_floats[25:36], 0)
mean4_xy = np.mean(data_floats[36:47], 0)

var1_xy = np.var(data_floats[:11], 0)
var2_xy = np.var(data_floats[12:23], 0)
var3_xy = np.var(data_floats[25:36], 0)
var4_xy = np.var(data_floats[36:47], 0)


list_of_means = [mean1_xy, mean2_xy, mean3_xy, mean4_xy]
list_of_vars = [var1_xy, var2_xy, var3_xy, var4_xy]
for list1 in list_of_means:
    for num in list1:
        #print("{:10.2f}".format(num))
        2+2

corr1 = pearsonr(data_floats[:11, 0],  data_floats[:11,1]).statistic.round(2)
corr2 = pearsonr(data_floats[12:23, 0],  data_floats[12:23,1]).statistic.round(2)
corr3 = pearsonr(data_floats[25:36, 0],  data_floats[25:36,1]).statistic.round(2)
corr4 = pearsonr(data_floats[36:47, 0],  data_floats[36:47,1]).statistic.round(2)

slope, intercept, r_value, p_value, std_err = stats.linregress(list(data_floats[:11, 0]), list(data_floats[:11,1]))
#slope, intercept, r_value, p_value, std_err = stats.linregress(list(data_floats[25:36, 0]), list(data_floats[25:36,1]))



plt.rcParams["figure.figsize"] = [7.50, 3.50]
plt.rcParams["figure.autolayout"] = True

def f(x):
   return slope*x + intercept

x = np.linspace(-10, 10, 100)

plt.plot(x, f(x), color='red')

plt.show()

