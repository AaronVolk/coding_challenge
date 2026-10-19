from logging import DEBUG, INFO, WARNING, ERROR, CRITICAL

MAX_POTENT_COUNTS: int = 255  #  Maximum potentiometer reading for one full rotation
GEAR_RATIO: int | float = 30  # gear ratio between the encoder and the shaft
ENCODER_CYCLES_PER_REV: int | float = 2048  # The amount of encoder counts for one full revolution of the motor
CALIBRATION_TIME: int | float = .5  # time used to calibrate sensors

THRESHOLD_Z_SCORE: int | float = 6.1911 # The largest Z score a reading can have before being considered faulty
LOG_LEVEL: int = INFO  # how much information the log will print