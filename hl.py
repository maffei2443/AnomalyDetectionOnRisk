import numpy as np
import matplotlib.pyplot as plt 
from numpy import genfromtxt
import datetime

import aux as A
import os
os.makedirs(A.OUTPUT_IMG/'hl', exist_ok=True,)

# The HardLimits class is capable of fetching data, performing anomaly detection on said data,
# calculates the score and plot the result.
class hl(): 

    def HL(self, data):        
        λ = .07

        UCL = np.empty_like(data)
        LCL = np.empty_like(data)
        for i in range(0,len(data)):
            UCL[i] = data[i] + λ*abs(data[i])
            LCL[i] = data[i] - λ*abs(data[i])

        return UCL, LCL


    #Expected three tensorflow matrices of datapoints.
    #Runs the AD and prints results.
    def runAnomalyDetection(self, D, D_truth, D_unpolluted, dataType, dataSize):
        FP = 0.
        FN = 0.
        TP = 0.
        TN = 0.

        FN_ALO = 0.
        TP_ALO = 0.
        FN_LS = 0.
        TP_LS = 0.
        FN_TC = 0.
        TP_TC = 0.
        FN_LTO = 0.
        TP_LTO = 0.
        FN_SALO = 0.
        TP_SALO = 0.


        reaction_counter = 0.
        tot_reaction = 0.


        print("Running Hardlimits-AD")
        guessed_anomalies = np.zeros((len(D), len(D[0])))
        for i in range(len(D)):
            UCL, LCL = self.HL(D[i])
            for t in range(int(0.1*len(D[i])), len(D[i])):
                if  UCL[t-1] < D[i][t] or D[i][t] < LCL[t-1]:
                    guessed_anomalies[i][t] = 1 #This is an anomaly guess


            #Evaluate
            in_anomaly_window = False
            anomaly_window_type = 0
            has_flagged_anomaly_window = False
            for t in range(1, len(D[i])):

                #Exiting an anomaly window. Check if it has been flagged.
                if D_truth[i][t] == 0 and in_anomaly_window:
                    in_anomaly_window = False
                    if not has_flagged_anomaly_window: 
                        FN += 1 #Failed to flag the entire anomaly window.
                        if int(anomaly_window_type) == 1:
                            FN_ALO += 1 #Failed to flag the entire anomaly window.
                        elif int(anomaly_window_type) == 2:
                            FN_LS += 1 #Failed to flag the entire anomaly window.
                        elif int(anomaly_window_type) == 3:
                            FN_TC += 1 #Failed to flag the entire anomaly window.
                        elif int(anomaly_window_type) == 4:
                            FN_LTO += 1 #Failed to flag the entire anomaly window.
                        elif int(anomaly_window_type) == 5:
                            FN_SALO += 1 #Failed to flag the entire anomaly window.
                        else:
                            print("ERROR ANOMALY WINDOW  HAD NO TYPE!")
                            print(int(anomaly_window_type))
                    else:
                        has_flagged_anomaly_window = False
                    reaction_counter = 0.
                #Entering an anomaly window.
                if D_truth[i][t] != 0 and not in_anomaly_window:
                    in_anomaly_window = True
                    anomaly_window_type = D_truth[i][t]

                if guessed_anomalies[i][t] == 0 and not in_anomaly_window:
                    TN += 1 #Correct to not guess for an anomaly.
                if guessed_anomalies[i][t] != 0 and in_anomaly_window and not has_flagged_anomaly_window:
                    TP += 1 #Correct guess, within anomaly window.
                    tot_reaction += reaction_counter #Add reaction counter to av
                    reaction_counter = 0.
                    has_flagged_anomaly_window = True
                    if int(anomaly_window_type) == 1:
                        TP_ALO += 1 
                    elif int(anomaly_window_type) == 2:
                        TP_LS += 1 
                    elif int(anomaly_window_type) == 3:
                        TP_TC += 1 
                    elif int(anomaly_window_type) == 4:
                        TP_LTO += 1 
                    elif int(anomaly_window_type) == 5:
                        TP_SALO += 1 
                    else:
                        print("ERROR ANOMALY WINDOW  HAD NO TYPE!")
                        print(int(anomaly_window_type))
                if guessed_anomalies[i][t] != 0 and not in_anomaly_window:
                    FP += 1 #Erroneous guess, outside anomaly window.
                if guessed_anomalies[i][t] == 0 and in_anomaly_window and not has_flagged_anomaly_window:
                    reaction_counter += 1 #Failed to react to an anomaly which was present in the current timestep.

        print("|" + "TP: " + str(TP) + "|TN: " + str(TN) +  "|" + "FP: " + str(FP) + "|" + "FN: " + str(FN) + "|")
        precision = TP / (TP + FP + 0.000000001)
        recall = TP / (TP + FN)

        avg_reaction = tot_reaction/(TP + 0.000000001)

        if precision == 0 and recall == 0:
            print("Somethings is wrong. No TP's")
            precision = 0.0000001
            recall = 0.00000001

        F1 = 2* (precision * recall) / (precision + recall)
        print("Anomalies:   " + str(TP + FN))
        print("Guesses:     " + str(TP + FP))
        print("precision:   " + str(precision))
        print("recall:      " + str(recall))
        print("F1:          " + str(F1))
        print("Reaction:    " + str(avg_reaction))
        print("TP_ALO:      " + str(TP_ALO))
        print("FN_ALO:      " + str(FN_ALO))
        print("TP_LS:       " + str(TP_LS))
        print("FN_LS:       " + str(FN_LS))
        print("TP_TC:       " + str(TP_TC))
        print("FN_TC:       " + str(FN_TC))
        print("TP_LTO:      " + str(TP_LTO))
        print("FN_LTO:      " + str(FN_LTO))
        print("TP_SALO:     " + str(TP_SALO))
        print("FN_SALO:     " + str(FN_SALO))

        with open(str(dataType) + "_" + str(dataSize) + '_result_hl.txt', 'a') as the_result_file:
            the_result_file.write("\n\n\n")
            the_result_file.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
            the_result_file.write("\n")
            the_result_file.write("|" + "TP: " + str(TP) + "|TN: " + str(TN) +  "|" + "FP: " + str(FP) + "|" + "FN: " + str(FN) + "|")
            the_result_file.write("\nAnomalies:   " + str(TP + FN))
            the_result_file.write("\nGuesses:     " + str(TP + FP))
            the_result_file.write("\nprecision:   " + str(precision))
            the_result_file.write("\nrecall:      " + str(recall))
            the_result_file.write("\nF1:          " + str(F1))
            the_result_file.write("\nReaction:    " + str(avg_reaction))
            the_result_file.write("\nTP_ALO:      " + str(TP_ALO))
            the_result_file.write("\nFN_ALO:      " + str(FN_ALO))
            the_result_file.write("\nTP_LS:       " + str(TP_LS))
            the_result_file.write("\nFN_LS:       " + str(FN_LS))
            the_result_file.write("\nTP_TC:       " + str(TP_TC))
            the_result_file.write("\nFN_TC:       " + str(FN_TC))
            the_result_file.write("\nTP_LTO:      " + str(TP_LTO))
            the_result_file.write("\nFN_LTO:      " + str(FN_LTO))
            the_result_file.write("\nTP_SALO:     " + str(TP_SALO))
            the_result_file.write("\nFN_SALO:     " + str(FN_SALO))



        return guessed_anomalies


    def plotAnomalyDetection(self, D, D_truth, D_unpolluted, D_guesses = None):
        if D_guesses is None:
            D_guesses = np.zeros((len(D), len(D[0])))

        
        for sample_nr in range(min(len(D),10)):
            UCL, LCL = self.HL(D[sample_nr])

            x = range(len(D[sample_nr]))

            at = np.trim_zeros(D_truth[sample_nr])
            UCL = np.insert(UCL, 0, np.mean(UCL))
            UCL = np.delete(UCL, -1)
            LCL = np.insert(LCL, 0, np.mean(LCL))
            LCL = np.delete(LCL, -1)
            
            plt.fill_between(x, UCL, LCL, facecolor='green', alpha=0.4)
            all_gi = np.argwhere(D_guesses[sample_nr] != 0) #all guesses
            all_ai = np.argwhere(D_truth[sample_nr] != 0)   #all actuall anomalies
            for gi in all_gi:
                dot_wrong, = plt.plot(gi, D[sample_nr][gi], 'yo', label='Incorrect Guess')
                #plt.axvspan(ai-0.1, ai+0.1, facecolor='#990000', alpha=0.8)
            for ai in all_ai:
                dot_actual, = plt.plot(ai, D[sample_nr][ai], 'ro', label='Anomaly')
                if ai in all_gi:
                    dot_correct, = plt.plot(ai, D[sample_nr][ai], 'ko', label='Correct Guess')
                #plt.axvspan(ai-0.1, ai+0.1, facecolor='#990000', alpha=0.8)
            line_actual, = plt.plot(D[sample_nr], 'r-', label='True Values')
            line_unpolluted, = plt.plot(D_unpolluted[sample_nr], label='True Values without Anomalies')
            plt.axvline(x=int(len(D[sample_nr])*0.1), color='grey')

            plt.title("HL on anomlies that are present in this serie: " + str(np.unique(at)))

            plt.legend(handles=[line_actual, line_unpolluted, dot_wrong, dot_actual, dot_correct])
            plt.show(block=False)
            plt.savefig(A.OUTPUT_IMG/'hl'/f'{sample_nr}.png')
            plt.close()
            

