import numpy as np
import matplotlib.pyplot as plt

amount_of_logs = 600  # number of picture processes done, until a graph is plotted
total_data = []


def plot_data(data):
    total_data.append(data)

    if len(total_data) == amount_of_logs:
        new_total_data = total_data[100:]
        plt.plot(np.arange(0, len(new_total_data)), np.array(new_total_data), 'o')
        plt.axhline(y=np.nanmean(np.array(new_total_data)), color='red', linewidth=2)
        plt.show()
