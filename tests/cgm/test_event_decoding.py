import unittest
import base64
import struct
from decocare import lib
from decocare import cgm

class TestEventDecoding(unittest.TestCase):
  SENSOR_TIMESTAMP_REFERENCE = '1028B61408'

  def make_into_page(self, bytes):
    page = bytearray(base64.b16decode(bytes))
    while len(page) < 1022:
      page.append(0x00)
    crc = lib.CRC16CCITT.compute(page)
    page.extend([crc >> 8 & 0xFF, crc & 0xFF])
    return page

  def test_page_end(self):
    page = self.make_into_page('01')
    records = cgm.PagedData.Data(page).decode()
    self.assertEqual(records[0]['name'], 'DataEnd')

  def test_sensor_weak_signal(self):
    page = self.make_into_page('02' + self.SENSOR_TIMESTAMP_REFERENCE)
    records = cgm.PagedData.Data(page).decode()
    self.assertEqual(records[0]['name'], 'SensorWeakSignal')
    self.assertEqual(records[0]['date'], '2016-02-08T20:54:00')

  def test_sensor_calibration_meter_bg_now(self):
    page = self.make_into_page('0003' + self.SENSOR_TIMESTAMP_REFERENCE)
    records = cgm.PagedData.Data(page).decode()
    self.assertEqual(records[0]['name'], 'SensorCal')
    self.assertEqual(records[0]['date'], '2016-02-08T20:54:00')
    self.assertEqual(records[0]['calibration_type'], 'meter_bg_now')

  def test_sensor_calibration_waiting(self):
    page = self.make_into_page('0103' + self.SENSOR_TIMESTAMP_REFERENCE)
    records = cgm.PagedData.Data(page).decode()
    self.assertEqual(records[0]['name'], 'SensorCal')
    self.assertEqual(records[0]['date'], '2016-02-08T20:54:00')
    self.assertEqual(records[0]['calibration_type'], 'waiting')

  def test_sensor_calibration_cal_error(self):
    page = self.make_into_page('0203' + self.SENSOR_TIMESTAMP_REFERENCE)
    records = cgm.PagedData.Data(page).decode()
    self.assertEqual(records[0]['name'], 'SensorCal')
    self.assertEqual(records[0]['date'], '2016-02-08T20:54:00')
    self.assertEqual(records[0]['calibration_type'], 'cal_error')

  def test_sensor_packet(self):
    page = self.make_into_page('0204' + self.SENSOR_TIMESTAMP_REFERENCE)
    records = cgm.PagedData.Data(page).decode()
    self.assertEqual(records[0]['name'], 'SensorPacket')
    self.assertEqual(records[0]['date'], '2016-02-08T20:54:00')

  def test_sensor_error_end(self):
    page = self.make_into_page('0105' + self.SENSOR_TIMESTAMP_REFERENCE)
    records = cgm.PagedData.Data(page).decode()
    self.assertEqual(records[0]['name'], 'SensorError')
    self.assertEqual(records[0]['date'], '2016-02-08T20:54:00')
    self.assertEqual(records[0]['error_type'], 'end')

  def test_sensor_data_low(self):
    page = self.make_into_page('06' + self.SENSOR_TIMESTAMP_REFERENCE)
    records = cgm.PagedData.Data(page).decode()
    self.assertEqual(records[0]['name'], 'GlucoseSensorDataLow')
    self.assertEqual(records[0]['date'], '2016-02-08T20:54:00')
    self.assertEqual(records[0]['sgv'], 40)

  def test_sensor_data_high(self):
    page = self.make_into_page('0007' + self.SENSOR_TIMESTAMP_REFERENCE)
    records = cgm.PagedData.Data(page).decode()
    self.assertEqual(records[0]['name'], 'GlucoseSensorDataHigh')
    self.assertEqual(records[0]['date'], '2016-02-08T20:54:00')
    self.assertEqual(records[0]['sgv'], 400)

  def test_sensor_timestamp_page_end(self):
    page = self.make_into_page('1028B61408')
    records = cgm.PagedData.Data(page).decode()
    self.assertEqual(len(records), 1)
    self.assertEqual(records[0]['name'], 'SensorTimestamp')
    self.assertEqual(records[0]['date'], '2016-02-08T20:54:00')
    self.assertEqual(records[0]['timestamp_type'], 'page_end')

  def test_sensor_timestamp_last_rf(self):
    page = self.make_into_page('1008B61408')
    records = cgm.PagedData.Data(page).decode()
    self.assertEqual(records[0]['name'], 'SensorTimestamp')
    self.assertEqual(records[0]['date'], '2016-02-08T20:54:00')
    self.assertEqual(records[0]['timestamp_type'], 'last_rf')

  def test_sensor_timestamp_gap(self):
    page = self.make_into_page('1048B61408')
    records = cgm.PagedData.Data(page).decode()
    self.assertEqual(records[0]['name'], 'SensorTimestamp')
    self.assertEqual(records[0]['date'], '2016-02-08T20:54:00')
    self.assertEqual(records[0]['timestamp_type'], 'gap')

  def testbattery_change(self):
    page = self.make_into_page('0E0AAE0B0A')
    records = cgm.PagedData.Data(page).decode()
    self.assertEqual(records[0]['name'], 'BatteryChange')
    self.assertEqual(records[0]['date'], '2014-02-10T11:46:00')

  def test_sensor_status_off(self):
    page = self.make_into_page('1008B6140B')
    records = cgm.PagedData.Data(page).decode()
    self.assertEqual(records[0]['name'], 'SensorStatus')
    self.assertEqual(records[0]['date'], '2016-02-08T20:54:00')
    self.assertEqual(records[0]['status_type'], 'off')

  def test_sensor_status_on(self):
    page = self.make_into_page('1028B6140B')
    records = cgm.PagedData.Data(page).decode()
    self.assertEqual(records[0]['name'], 'SensorStatus')
    self.assertEqual(records[0]['date'], '2016-02-08T20:54:00')
    self.assertEqual(records[0]['status_type'], 'on')

  def test_sensor_status_lost(self):
    page = self.make_into_page('1048B6140B')
    records = cgm.PagedData.Data(page).decode()
    self.assertEqual(records[0]['name'], 'SensorStatus')
    self.assertEqual(records[0]['date'], '2016-02-08T20:54:00')
    self.assertEqual(records[0]['status_type'], 'lost')

  def test_datetime_change(self):
    page = self.make_into_page('0E3ED20A0C')
    records = cgm.PagedData.Data(page).decode()
    self.assertEqual(records[0]['name'], 'DateTimeChange')
    self.assertEqual(records[0]['date'], '2014-03-30T10:18:00')

  def test_sensor_sync_new(self):
    page = self.make_into_page('0F33444D0D')
    records = cgm.PagedData.Data(page).decode()
    self.assertEqual(records[0]['name'], 'SensorSync')
    self.assertEqual(records[0]['date'], '2015-05-19T13:04:00')
    self.assertEqual(records[0]['sync_type'], 'new')

  def test_sensor_sync_old(self):
    page = self.make_into_page('0F53444D0D')
    records = cgm.PagedData.Data(page).decode()
    self.assertEqual(records[0]['name'], 'SensorSync')
    self.assertEqual(records[0]['date'], '2015-05-19T13:04:00')
    self.assertEqual(records[0]['sync_type'], 'old')

  def test_sensor_sync_find(self):
    page = self.make_into_page('0F73444D0D')
    records = cgm.PagedData.Data(page).decode()
    self.assertEqual(records[0]['name'], 'SensorSync')
    self.assertEqual(records[0]['date'], '2015-05-19T13:04:00')
    self.assertEqual(records[0]['sync_type'], 'find')

  def test_cal_bg_for_gh(self):
    page = self.make_into_page('A08F135B4F0E')
    records = cgm.PagedData.Data(page).decode()
    self.assertEqual(records[0]['name'], 'CalBGForGH')
    self.assertEqual(records[0]['date'], '2015-05-19T15:27:00')
    self.assertEqual(records[0]['amount'], 160)

  def test_sensor_calibration_factor(self):
    page = self.make_into_page('8C120F13674F0F')
    records = cgm.PagedData.Data(page).decode()
    self.assertEqual(records[0]['name'], 'SensorCalFactor')
    self.assertEqual(records[0]['date'], '2015-05-19T15:39:00')
    self.assertEqual(records[0]['factor'], 4.748)

  def test_ten_something(self):
    page = self.make_into_page('0000020E0AB40B10')
    records = cgm.PagedData.Data(page).decode()
    self.assertEqual(records[0]['name'], '10-Something')
    self.assertEqual(records[0]['date'], '2014-02-10T11:52:00')

if __name__ == '__main__':
  unittest.main()
