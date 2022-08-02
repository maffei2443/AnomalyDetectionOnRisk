from pathlib import Path
import os


OUTPUT_IMG=Path('OUTPUT')
os.makedirs(OUTPUT_IMG, exist_ok=True)

def update_anom(D, D_truth, i, ):
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
  return in_anomaly_window, anomaly_window_type, has