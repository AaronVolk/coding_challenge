from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL

MAX_VOLTAGE: int = 255  # When the shaft completes one full rotation (360*), the sensor reads 255.
GEAR_RATIO: int | float = 30  # gear ratio between the encoder and the shaft
ENCODER_CYCLES_PER_REV: int | float = 2048  # The amount of counts for one full revolution of the encoder
CALIBRATION_TIME: int | float = .5  # time where the gearbox is guaranteed to work

THRESHOLD_Z_SCORE: int | float = 6.1911 # The largest Z score a reading can have before being considered faulty (determined using find_threshold.py)
LOG_LEVEL: int = INFO  # how much information the log will print