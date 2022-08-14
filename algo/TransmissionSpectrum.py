'''
created at 14/08/22

@author: Assaf S.
'''

# This Class plots a transmition spectrum for the chip
# Tasks:
# 1. read each i'th (i=5) csv file to an array
# 2. attach arrays
# 3. plot

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np


class TransmissionSpectrum():
    def __init__(self,directory):
        """"""
        self.directory = directory
        self.spectrum_parts = []
        self.total_spectrum = []
        for i in range(2, 70, 5):
            if i<10:
                filename = '20220814_-_20to80fsr_-_40mw_-_777-779~_0'+str(i)+'.csv'
            else:
                filename = '20220814_-_20to80fsr_-_40mw_-_777-779~_' + str(i) + '.csv'

            full_path = self.directory+'//'+ filename
            self.spectrum_parts.append(self.read_csv(full_path)[2:])

        self.total_spectrum = np.concatenate(self.spectrum_parts)
        self.total_spectrum = [item[1] for item in self.total_spectrum]
        self.total_spectrum = [float(item) for item in self.total_spectrum]

    def piezo_scan_spectrum(self, i):
        if i < 10:
            filename = '20220814_-_20to80fsr_-_40mw_-_777-779~_0' + str(i) + '.csv'
        else:
            filename = '20220814_-_20to80fsr_-_40mw_-_777-779~_' + str(i) + '.csv'
        full_path = self.directory + '//' + filename
        self.piezo_scan = self.read_csv(full_path)[2:]
        self.piezo_scan = [item[1] for item in self.piezo_scan]
        self.piezo_scan = [float(item) for item in self.piezo_scan]
        return self.piezo_scan

    def read_csv(self, filename):
        csv_data = pd.read_csv(filename, sep=',', header=None)
        return csv_data.values
    def plot_spectrum(self,Y,num_of_plots):
        # Create Figure and Axes instances
        if num_of_plots>1:
            fig = plt.figure()
            ax1 = fig.add_axes(
                               xticklabels=[], ylim=(-10, 10))
            ax2 = fig.add_axes(
                               ylim=(-10, 10))
            ax1.plot(Y[0])
            ax2.plot(Y[1])
        else:
            # Make your plot, set your axes labels
            ax.plot(Y)
        plt.show()

    def save_figure(self,dist_name):
        plt.savefig(dist_name)

if __name__ == "__main__":
    o=TransmissionSpectrum('20220814_777-779')
    scan_spectrum = []
    for i in range (2,6):
        scan_spectrum += [o.piezo_scan_spectrum(i)]
    o.plot_spectrum(scan_spectrum,2)
        #o.plot_spectrum(self.total_spectrum[::1000])
        #o.save_figure('fig_'+str(i))