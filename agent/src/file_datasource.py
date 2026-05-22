from csv import reader, DictReader
from datetime import datetime
from io import StringIO
from typing import TextIO

import config
from domain.accelerometer import Accelerometer
from domain.aggregated_data import AggregatedData
from domain.gps import Gps
from domain.aq import Aq


class FileDatasource:
    def __init__(self, accelerometer_filename: str, gps_filename: str, qc_filename: str):
        self.gps_file = None
        self.accelerometer_file = None
        self.aq_file = None
        self.aq_filename = qc_filename
        self.accelerometer_filename = accelerometer_filename
        self.gps_filename = gps_filename



    def read(self) -> AggregatedData:
        self.checkFilesReadable()
        accelerometerReader = reader(self.accelerometer_file)
        accelerometerRow = next(accelerometerReader)
        gps = ''
        accelerometer = ''
        aq = ''
        if not self.isHeader(accelerometerRow):
            accelerometer = Accelerometer(int(accelerometerRow[0]), int(accelerometerRow[1]), int(accelerometerRow[2]))

        gpsReader = reader(self.gps_file)
        gpsRow = next(gpsReader)
        if not self.isHeader(gpsRow):
            gps = Gps(float(gpsRow[0]), float(gpsRow[1]))

        aqReader = reader(self.aq_file)
        aqRow = next(aqReader)
        if not self.isHeader(aqRow):
            aq = Aq(int(aqRow[0]), int(aqRow[1]), int(aqRow[2]), int(aqRow[3]))

        return AggregatedData(accelerometer, gps, aq, datetime.now(), config.USER_ID)

    def isHeader(self, row):
        if row[0].isdigit():
            return False
        try:
            float(row[0])
            return False
        except ValueError:
            return True


    def checkFilesReadable(self):
        if not self.accelerometer_file.readable() and self.accelerometer_file and  not self.accelerometer_file.closed:
            print("Something went wrong during opening file: ", self.accelerometer_file.name)
        if not self.gps_file.readable() and self.gps_file and  not self.gps_file.closed:
            print("Something went wrong during opening file: ", self.gps_file.name)
        if not self.aq_file.readable() and self.aq_file and  not self.aq_file.closed:
            print("Something went wrong during opening file: ", self.aq_file.name)

    def startReading(self, *args, **kwargs):
        accelerometer_file = open(self.accelerometer_filename, newline='')
        gps_file = open(self.gps_filename, newline='')
        aq_file = open(self.aq_filename, newline='')
        self.accelerometer_file = accelerometer_file
        self.gps_file = gps_file
        self.aq_file = aq_file
        self.checkFilesReadable()

    def stopReading(self, *args, **kwargs):
        self.accelerometer_file.close()
        self.gps_file.close()
        self.aq_file.close()


