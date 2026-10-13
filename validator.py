import config
import logging
from statistics import mean, median, stdev
from pprint import pformat

class Reading:
    def __init__(self, time: float, encoder: int, pot: int):
        """
        Basic class to store the readings found in the input files

        ATTRIBUTES:
            time: the time of the reading
            encoder: value of the encoder reading
            pot: value of the potentiometer reading
        """
        self.time = time
        self.encoder = encoder
        self.pot = pot

    @classmethod
    def from_input_file(cls, line: str):
        """
        class method to parse a line of the input file directly

        ARGUMENTS:
            a line of the input file
        """
        line = line.split()
        return cls(float(line[0]), int(line[1]), int(line[2]))

    def __str__(self):
        return f"time = {self.time}s: encoder degrees: {self.encoder:.3f}, pot degrees: {self.pot:.3f}"

    def __repr__(self):
        return str(self)


class Validator:
    data: list[Reading] | None  # list of all sensor readings from the file
    _calibration_time: int | float  # time when gearbox is reported to work properly

    _noise_floor: float  # the smallest sensor difference that indicates a problem, based on potentiometer
    _threshold: int | float  # how unusual a reading can be before it is considered faulty

    _std_dev: float  # how much the sensors differ during calibration
    _mean: float  # the average difference between the sensors during calibration

    _logger: logging.Logger

    def __init__(self,
                 input_path: str,
                 max_voltage: int = config.MAX_VOLTAGE,
                 gear_ratio: int | float = config.GEAR_RATIO,
                 encoder_cycles: int | float = config.ENCODER_CYCLES_PER_REV,
                 threshold: int | float = config.THRESHOLD_Z_SCORE,
                 calibration_time: int | float = config.CALIBRATION_TIME
                 ):
        """
        Class that takes an input file of potentiometer and encoder readings from a gearbox and then validates whether the
        sensor's readings are faulty.

        ARGUMENTS:
            input_path: the path to the input file of potentiometer and encoder readings
            max_voltage: potentiometer A/D reading from the shaft being at 360 degrees (defaults to config.MAX_VOLTAGE)
            gear ratio: gear ratio between the encoder and the shaft (defaults to config.GEAR_RATIO)
            encoder_cycles: The amount of counts for one full revolution of the encoder (defaults to config.ENCODER_CYCLES_PER_REV)
            threshold: The largest Z score a reading can have before being considered faulty (defaults to config.THRESHOLD_Z_SCORE)
        """
        self._logger = logging.getLogger("Validator")

        # define the stuff given to us
        self._noise_floor = 360 / max_voltage  # the smallest change in shaft position the pot can detect
        self._threshold = threshold
        self._calibration_time = calibration_time

        # get the data from the input file and then convert the readings into shaft position
        try:
            with open(input_path) as f:
                raw_data = f.read().splitlines()
            self.data = self._clean_data(raw_data, max_voltage, gear_ratio, encoder_cycles)
        except FileNotFoundError:
                self._logger.error(f"file {input_path} not found. Cannot create object")
                self.data = None
                return
        except:
            self._logger.exception(f"unexpected error while parsing {input_path}:")
            self.data = None
            return
        self._logger.debug(f"data from {input_path}:\n{pformat(self.data)}")

        self._statistic_analysis()
        self._logger.debug(f"standard deviation of disagreement during normal operation: {self._std_dev}\nthreshold: {self._threshold}")

    def _z_score(self, x):
        return abs((x - self._mean) / max(self._std_dev, self._noise_floor))

    def _clean_data(self, data: list[str], max_voltage, gear_ratio, encoder_cycles) -> list[Reading]:
        """
        takes the raw data of the input file and uses the functional relationships of the sensors readings to the shaft
        position and converts the readings to the position of the shaft.

        ARGUMENTS:
            data: data from the input file, split into a list of each line of readings
            max_voltage: the voltage of the potentiometer when the shaft is at 360 degrees
            gear ratio: gear ratio between the encoder and the shaft
            encoder_cycles: The amount of counts for one full revolution of the encoder

        RETURNS:
            a list of absolute readings of where the pot and encoder think the shaft is

        """
        # small functions that convert sensor readings into degrees.
        convert_pot = lambda voltage: voltage / (max_voltage / 360)
        convert_encoder = lambda encoder: (360 / (gear_ratio * encoder_cycles)) * encoder

        # Turns the file's data into reading objects and converts their values into degrees.
        data = [Reading.from_input_file(line) for line in data]
        for reading in data:
            reading.encoder = convert_encoder(reading.encoder)
            reading.pot = convert_pot(reading.pot)

        # The two sensors might not show exactly the same position, even when both are working correctly.
        # The program compares their readings to find the difference
        offset_slice = [(reading.pot - reading.encoder) for reading in data if (reading.time <= self._calibration_time)]
        offset = median(offset_slice)  # use the median instead of mean to minimize noise
        self._logger.debug(f"offset = {offset: .4f}")

        for reading in data: reading.encoder += offset  # Adjust the encoder readings to match the shaft's actual position.
        return data

    def _statistic_analysis(self):
        """
        uses the data at time = [0, calibration_time] to determine the standard deviation of the disagreement of the
        readings when the gearbox is guaranteed to be in working order

        RETURNS:
            the standard deviation of the disagreement between the readings
        """
        if self.data is None: raise TypeError("data is None")
        disagreement_slice = [  # Calculate the difference between the two sensor readings by subtracting them
            abs(reading.pot - reading.encoder) for reading in self.data if (reading.time <= self._calibration_time)
        ]

        self._mean = mean(disagreement_slice)
        self._std_dev = stdev(disagreement_slice)

    def validate(self) -> Reading | None:
        """
        Validates whether the sensors are faulty or not

        RETURNS:
            the reading where a fault is detected if the sensors are failing. None otherwise
        """
        if self.data is None: raise TypeError("data is None")

        # Ignore the calibration period when checking for faults because the gearbox is expected to work properly then.
        validation_set = [reading for reading in self.data if (reading.time > self._calibration_time)]

        for reading in validation_set:
            disagreement = abs(reading.encoder - reading.pot)

            # Use the larger value to make sure normal sensor differences caused by measurement limits aren't mistakenly flagged as faults.
            z_score = self._z_score(disagreement)

            self._logger.debug(f"time = {reading.time}: disagreement = {disagreement: .4f}, z_score = {z_score: .4f}")

            if z_score > self._threshold:
                return reading

        return None