import numpy as np
import matplotlib.pyplot as plt

amount_of_logs = 10000
total_data = []


def plot_data(data):
    total_data.append(data)

    if len(total_data) == amount_of_logs:
        plt.plot(np.arange(0, len(total_data)), np.array(total_data), 'o')
        plt.show()
