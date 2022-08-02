"""
This program runs the anomaly detection for EWMA, ARMA-GARCH and LSTM.
The program thereafter calculates the relevant scores.
"""
import sys
import time
import numpy as np

import ewma as E 
import hl as H
import lstm_tbptt_hyperopt as LS
import arma_garch as AG

from pathlib import Path

OUTPUT = Path('output')

#Function that loads data into a numpy matrix from csv file.
#These files are generated by running ./garch/garch_long.py
def getData(datatype="D1", size="100"):
    D = np.genfromtxt('./garch/' + datatype + '_' + size + '.csv', delimiter=',')
    D_no_anomalies = np.genfromtxt('./garch/' + datatype + '_unpolluted_' + size + '.csv', delimiter=',')
    D_truth = np.genfromtxt('./garch/' + datatype + '_truth_' + size + '.csv', delimiter=',')
    return D, D_no_anomalies, D_truth


if __name__ == "__main__":

    plot = False
    args = sys.argv[1:]
    if "--plot" in args:
        plot = True


    hl = H.hl()
    ewma = E.ewma()
    lstm = LS.lstm_tbptt()
    arma_garch = AG.arma_garch()

    start_sample = 0 # first serie to evaluate
    N = 6 # number of series to evaluate.


    dataTypes = ["D1", "D2", "D4"]
    dataSizes = ["5000"]


    for dt in dataTypes:
        for ds in dataSizes:
            #Get data from file.
            print("Starting Dataset:" + ds + " " + dt)
            D, D_no_anomalies, D_truth = getData(dt, ds)

            #HL
            start_hl = time.time()
            hl_guesses = hl.runAnomalyDetection(D[0:N], D_truth[0:N], D_no_anomalies[0:N], dt, ds)
            end_hl = time.time()
            np.savetxt(OUTPUT/str(dt) + "_" + str(ds) + "_guesses_hl.csv", hl_guesses, delimiter=",")
            print('Elapsed time for HL: ' + str(end_hl-start_hl))

            #EWMA
            start_ewma = time.time()
            ewma_guesses = ewma.runAnomalyDetection(D[0:N], D_truth[0:N], D_no_anomalies[0:N], dt, ds)
            end_ewma = time.time()
            np.savetxt(OUTPUT/str(dt) + "_" + str(ds) + "_guesses_ewma.csv", ewma_guesses, delimiter=",")
            print('Elapsed time for EWMA: ' + str(end_ewma-start_ewma))

            #ARMA
            start_arma = time.time()
            arma_garch_guesses, arma_garch_means, arma_garch_variances = arma_garch.runAnomalyDetection(D[0:N], D_truth[0:N], D_no_anomalies[0:N], dt, ds)
            end_arma = time.time()
            np.savetxt(OUTPUT/str(dt) + "_" + str(ds) + "_guesses_arma.csv", arma_garch_guesses, delimiter=",")
            print('Elapsed time for ARMA: ' + str(end_arma-start_arma))


            #LSTM
            start_lstm = time.time()
            lstm_guesses, lstm_preds, lstm_likelihoods, lstm_resudials = lstm.runAnomalyDetection(D[start_sample:N], D_truth[start_sample:N], D_no_anomalies[start_sample:N], dt, ds)
            end_lstm = time.time()
            np.savetxt(OUTPUT/str(dt) + "_" + str(ds) + "_guesses_lstm.csv", lstm_guesses, delimiter=",")
            print('Elapsed time for LSTM: ' + str(end_lstm-start_lstm))


            

            if plot:
                print("Plotting")
                hl.plotAnomalyDetection(D[0:N], D_truth[0:N], D_no_anomalies[0:N], ewma_guesses[0:N])
                ewma.plotAnomalyDetection(D[0:N], D_truth[0:N], D_no_anomalies[0:N], ewma_guesses[0:N])
                lstm.plotAnomalyDetection(D[0:N], D_truth[0:N], D_no_anomalies[0:N], lstm_guesses[0:N], lstm_preds[0:N], lstm_likelihoods[0:N], lstm_resudials[0:N])
                arma_garch.plotAnomalyDetection(D[0:N], D_truth[0:N], D_no_anomalies[0:N], arma_garch_guesses[0:N], arma_garch_means[0:N], arma_garch_variances[0:N])




    
    

    

