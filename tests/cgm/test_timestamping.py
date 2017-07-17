import unittest
import base64
import struct
from decocare import lib
from decocare import cgm

class TestTimestamping(unittest.TestCase):
  SENSOR_TIMESTAMP_REFERENCE = '1028B61408'

  def make_into_page(self, bytes):
    page = bytearray(base64.b16decode(bytes))
    while len(page) < 1022:
      page.append(0x00)
    crc = lib.CRC16CCITT.compute(page)
    page.extend([crc >> 8 & 0xFF, crc & 0xFF])
    return page

  def test_correct_relative_offset(self):
    page = self.make_into_page('34451028B6140801')
    records = cgm.PagedData.Data(page).decode()

    self.assertEqual(records[0]['name'], 'GlucoseSensorData')
    self.assertEqual(records[0]['date'], '2016-02-08T20:49:00')
    self.assertEqual(records[0]['sgv'], 104)

    self.assertEqual(records[1]['name'], 'GlucoseSensorData')
    self.assertEqual(records[1]['date'], '2016-02-08T20:54:00')
    self.assertEqual(records[1]['sgv'], 138)

    self.assertEqual(records[2]['name'], 'SensorTimestamp')
    self.assertEqual(records[2]['date'], '2016-02-08T20:54:00')

  def test_forward_timestamping_when_reverse_not_available(self):
    page = self.make_into_page('1008B61408344501')
    paged_data = cgm.PagedData.Data(page)

    self.assertFalse(paged_data.needs_timestamp())

    records = paged_data.decode()

    self.assertEqual(records[0]['name'], 'SensorTimestamp')
    self.assertEqual(records[0]['date'], '2016-02-08T20:54:00')
    self.assertEqual(records[0]['timestamp_type'], 'last_rf')

    self.assertEqual(records[1]['name'], 'GlucoseSensorData')
    self.assertEqual(records[1]['date'], '2016-02-08T20:59:00')
    self.assertEqual(records[1]['sgv'], 104)

    self.assertEqual(records[2]['name'], 'GlucoseSensorData')
    self.assertEqual(records[2]['date'], '2016-02-08T21:04:00')
    self.assertEqual(records[2]['sgv'], 138)

  def test_no_forward_timestamp_when_timestamp_type_gap(self):
    page = self.make_into_page('1048B61408344501')
    paged_data = cgm.PagedData.Data(page)

    self.assertTrue(paged_data.needs_timestamp())

    records = paged_data.decode()

    self.assertEqual(records[0]['name'], 'SensorTimestamp')
    self.assertEqual(records[0]['date'], '2016-02-08T20:54:00')
    self.assertEqual(records[0]['timestamp_type'], 'gap')

    self.assertEqual(records[1]['name'], 'GlucoseSensorData')
    self.assertTrue('date' not in records[1])
    self.assertEqual(records[1]['sgv'], 104)

    self.assertEqual(records[2]['name'], 'GlucoseSensorData')
    self.assertTrue('date' not in records[2])
    self.assertEqual(records[2]['sgv'], 138)

  def test_no_forward_timestamp_when_independent_event_since_last_reference(self):
    page = self.make_into_page('1008B61408114501')
    paged_data = cgm.PagedData.Data(page)

    self.assertTrue(paged_data.needs_timestamp())

    records = paged_data.decode()

    self.assertEqual(records[0]['name'], 'SensorTimestamp')
    self.assertEqual(records[0]['date'], '2016-02-08T20:54:00')
    self.assertEqual(records[0]['timestamp_type'], 'last_rf')

    self.assertEqual(records[1]['name'], 'Could Not Decode')

    self.assertEqual(records[2]['name'], 'GlucoseSensorData')
    self.assertTrue('date' not in records[2])
    self.assertEqual(records[2]['sgv'], 138)

if __name__ == '__main__':
  unittest.main()
