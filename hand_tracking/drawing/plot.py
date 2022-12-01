import numpy as np
import matplotlib.pyplot as plt

amount_of_logs = 1100  # number of picture processes done, until a graph is plotted
starting_threshold = 100  # ignore the first 100 points
moving_average = 20  # moving average length

allowed_div = 0.2

total_data = []
average_data = []
index = []


def plot_data(data):
    total_data.append(data[0][2][2])
    average_data.append(np.mean(np.array(total_data[-moving_average:])))

    if (total_data[len(total_data)-1] > average_data[len(average_data)-1]*(1+allowed_div) or total_data[len(total_data)-1] < average_data[len(average_data)-1]*(1-allowed_div)) and len(total_data)-1 > starting_threshold:
        index.append(len(total_data)-1)

    if len(total_data) == amount_of_logs:
        for i in index:
            # plt.plot(i - starting_threshold, total_data[i], 'or')  # color breakouts red
            total_data[i] = average_data[i]  # set breakouts to average

        plt.plot(np.arange(0, len(total_data[starting_threshold:])), np.array(total_data[starting_threshold:]), 'o')
        plt.plot(np.arange(0, len(average_data[starting_threshold:])), np.array(average_data[starting_threshold:]))  # used for graphing the moving average
        # plt.axhline(y=np.nanmean(np.array(new_total_data)), color='red', linewidth=2)  # uncomment, if the average of the whole graph needs to be plotted

        for i in index:
            plt.plot(i - starting_threshold, total_data[i], 'or')  # color breakouts red




    plt.show()
