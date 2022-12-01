import numpy as np
import matplotlib.pyplot as plt

amount_of_logs = 200  # number of picture processes done, until a graph is plotted
moving_average = 20  # moving average length

total_data = []
average_data = []


def plot_data(data):
    total_data.append(data)
    average_data.append(np.mean(np.array(total_data[-moving_average:])))

    if len(total_data) == amount_of_logs:
        plt.plot(np.arange(0, len(total_data[100:])), np.array(total_data[100:]), 'o')
        plt.plot(np.arange(0, len(average_data[100:])), np.array(average_data[100:]))  # used for graphing the moving average
        # plt.axhline(y=np.nanmean(np.array(new_total_data)), color='red', linewidth=2)  # uncomment, if the average of the whole graph needs to be plotted

        plt.show()
