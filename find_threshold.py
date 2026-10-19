import config
from validator import Validator

validator = Validator("./input/normal.txt")

if validator.data is None:
    raise Exception("No data")  # if there is no data than the program stops running so warnings dont occur later
max_zscore = 0
worst_reading = None
for reading in validator.data:
    if reading.time <= config.CALIBRATION_TIME: continue

    disagreement = abs(reading.pot - reading.encoder)
    z_score = abs((disagreement - validator._mean) / validator._std_dev)
    if z_score > max_zscore:
        max_zscore = z_score
        worst_reading = reading


print("max_zscore:", max_zscore)
print("worst_reading:", worst_reading, abs(worst_reading.encoder - worst_reading.pot))