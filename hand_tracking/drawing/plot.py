import matplotlib.pyplot as plt
import numpy as np

amount_of_logs = 1100  # number of picture processes done, until a graph is plotted
starting_threshold = 100  # ignore the first 100 points
moving_average = 20  # moving average length

allowed_div = 0.2  # allowed deviation from average

total_data = []  # list to store data for plot
total_distance = []  # list to store distance for plot
average_data = []  # list to store moving average of data
index = []  # list to store indexes of data that deviate from moving average


def plot_data(data):
    # Append data of specific landmark to total_data
    total_data.append(data[0][2][2])

    # Calculate moving average of total_data and store it in average_data
    average_data.append(np.mean(np.array(total_data[-moving_average:])))

    # If current data point deviates more than allowed_div from moving average
    # and it is not in the starting_threshold, store its index in index
    if (total_data[len(total_data) - 1] > average_data[len(average_data) - 1] * (1 + allowed_div) or total_data[len(total_data) - 1] < average_data[len(average_data) - 1] * (1 - allowed_div)) and len(total_data) - 1 > starting_threshold:
        index.append(len(total_data) - 1)

    # If the number of data points reaches the amount_of_logs,
    # set data points that deviate from moving average to the moving average value
    # and plot the data
    if len(total_data) == amount_of_logs:
        for i in index:
            total_data[i] = average_data[i]  # set breakouts to average

        plt.plot(np.arange(0, len(total_data[starting_threshold:])), np.array(total_data[starting_threshold:]), 'o')

    plt.show()


def plot_distance(distance):
    # Append distance to total_distance
    total_distance.append(distance)

    # If the number of distance points reaches the amount_of_logs, plot the data
    if len(total_distance) == amount_of_logs:
        plt.plot(np.arange(0, len(total_distance[starting_threshold:])), np.array(total_distance[starting_threshold:]), 'or')
        plt.show()
