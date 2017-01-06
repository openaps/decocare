"""
cgm - package for decoding cgm pages

Maybe something like this?
* parse_time
* decoders - decoder classes?
* PageDecoder - stateful decoder
"""

from binascii import hexlify

# TODO: all this stuff could be refactored into re-usable and tested
# module.
import io
import copy
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dateutil import parser

from decocare import lib
from decocare.records import times
from decocare.errors import DataTransferCorruptionError
from pprint import pprint

class CgmDateDecoder (object):

  @classmethod
  def parse_date (klass, data, unmask=False, strict=False):
    data = data[:]
    seconds = 0
    minutes = 0
    hours   = 0

    year    = times.parse_years(data[3])
    day     = data[2] & 0x1F
    minutes = data[1] & 0b111111
    hours   = data[0] & 0x1F
    month   = ((data[0] & 0xC0) >> 4) + ((data[1] & 0xC0) >> 6)

    try:
      date = datetime(year, month, day, hours, minutes, seconds)
      return date
    except ValueError, e:
      if strict:
        raise
      if unmask:
        return (year, month, day, hours, minutes, seconds)
      pass
    return None

class PagedData (object):
  """
    PagedData - context for parsing a page of cgm data.
  """

  RECORDS = {
    0x01: dict(name='DataEnd',          packet_size=0, date_type='none',        op='0x01'),
    0x02: dict(name='SensorWeakSignal', packet_size=0, date_type='relative',    op='0x02'),
    0x03: dict(name='SensorCal',        packet_size=1, date_type='relative',    op='0x03'),
    0x04: dict(name='SensorPacket',     packet_size=1, date_type='relative',    op='0x04'),
    0x05: dict(name='SensorError',      packet_size=1, date_type='relative',    op='0x05'),
    0x06: dict(name='GlucoseSensorDataLow',    packet_size=0, date_type='relative',    op='0x06'),
    0x07: dict(name='GlucoseSensorDataHigh',   packet_size=1, date_type='relative',    op='0x07'),
    0x08: dict(name='SensorTimestamp',  packet_size=4, date_type='reference',   op='0x08'),
    0x0a: dict(name='BatteryChange',    packet_size=4, date_type='independent', op='0x0a'),
    0x0b: dict(name='SensorStatus',     packet_size=4, date_type='independent', op='0x0b'),
    0x0c: dict(name='DateTimeChange',   packet_size=4, date_type='independent', op='0x0c'),
    0x0d: dict(name='SensorSync',       packet_size=4, date_type='independent', op='0x0d'),
    0x0e: dict(name='CalBGForGH',       packet_size=5, date_type='independent', op='0x0e'),
    0x0f: dict(name='SensorCalFactor',  packet_size=6, date_type='independent', op='0x0f'),
    0x10: dict(name='10-Something',     packet_size=7, date_type='independent', op='0x10'),
    0x13: dict(name='19-Something',     packet_size=0, date_type='none',        op='0x13'),
  }

  @classmethod
  def Data (klass, data, **kwds):
    stream = io.BufferedReader(io.BytesIO(data))
    return klass(stream, **kwds)

  def __init__ (self, stream, larger=False):
    raw = bytearray(stream.read(1024))

    if len(raw) < 1024:
      raise DataTransferCorruptionError("Page size too short")

    data, expected_crc = raw[0:1022], raw[1022:]
    self.check_crc(data, expected_crc)

    data.reverse()

    self.larger = larger
    self.data = self.skip_null_bytes(data)

  def is_relative_record(self, record):
    return 'date_type' in record and record['date_type'] == 'relative'

  def needs_timestamp(self):
    return self.find_initial_timestamp() is None

  def decode (self):
    records = []
    timestamp = self.find_initial_timestamp()

    stream = self.stream_from_data(self.data)

    for B in iter(lambda: stream.read(1), ""):
      B = bytearray(B)
      record = self.decode_record(B[0], stream, timestamp)

      if record['name'] == 'SensorTimestamp':
        timestamp = parser.parse(record['date'])
      elif self.is_relative_record(record) and timestamp:
        timestamp = timestamp + relativedelta(minutes=-5)

      records.insert(0, record)

    self.records = records
    return self.records

  def decode_record (self, op, stream, timestamp):
    if self.larger:
      pass

    if op > 0 and op < 20:
      record = copy.deepcopy(self.RECORDS.get(op, None))
      if record is None:
        record = dict(name='Could Not Decode',packet_size=0,op=op)
    else:
      record = dict(name='GlucoseSensorData',packet_size=0,date_type='relative',op=op)
      record.update(sgv=(int(op) * 2))

    record['_tell'] = stream.tell( )

    if not record is None and record['packet_size'] > 0:
      # read the rest of record's bytes
      raw_packet = bytearray(stream.read(record['packet_size']))

    if record['name'] == 'SensorTimestamp':
      self.decode_sensor_timestamp(record, raw_packet)

    elif self.is_relative_record(record):
      if timestamp:
        record.update(date=timestamp.isoformat())

      if record['name'] == 'SensorCal':
        self.decode_sensor_calibration(record, raw_packet)
      elif record['name'] == 'SensorError':
        self.decode_sensor_error(record, raw_packet)
      elif record['name'] == 'GlucoseSensorDataLow':
        record.update(sgv=40)
      elif record['name'] == 'GlucoseSensorDataHigh':
        record.update(sgv=400)


    elif 'date_type' in record and record['date_type'] == 'independent':
      record.update(raw=self.byte_to_str(raw_packet))
      record.update(body=self.byte_to_str(raw_packet[4:]))

      date = CgmDateDecoder.parse_date(raw_packet[:4])
      if date is not None:
        record.update(date=date.isoformat())
      else:
        record.update(_date=str(raw_packet[:4]).encode('hex'))

      if record['name'] == 'CalBGForGH':
        self.decode_cal_bg_for_gh(record, raw_packet)
      if record['name'] == 'SensorCalFactor':
        self.decode_sensor_cal_factor(record, raw_packet)
      if record['name'] == 'SensorStatus':
        self.decode_sensor_status(record, raw_packet)
      if record['name'] == 'SensorSync':
        self.decode_sensor_sync(record, raw_packet)

    return record

  def decode_sensor_timestamp(self, record, raw_packet):
    record.update(raw=self.byte_to_str(raw_packet))

    raw_type = (raw_packet[2] & 0b01100000) >> 5
    if raw_type == 0x00:
      timestamp_type = 'last_rf'
    elif raw_type == 0x01:
      timestamp_type = 'page_end'
    elif raw_type == 0x02:
      timestamp_type = 'gap'
    else:
      timestamp_type = 'unknown'
    record.update(timestamp_type=timestamp_type)

    date = CgmDateDecoder.parse_date(raw_packet)
    if date is not None:
      record.update(date=date.isoformat())
    else:
      record.update(_date=str(raw_packet[:4]).encode('hex'))

  def decode_sensor_calibration(self, record, raw_packet):
    record.update(raw=self.byte_to_str(raw_packet))
    calibration_type = 'unknown'
    if raw_packet[0] == 0x00:
      calibration_type = 'meter_bg_now'
    if raw_packet[0] == 0x01:
      calibration_type = 'waiting'
    if raw_packet[0] == 0x02:
      calibration_type = 'cal_error'
    record.update(calibration_type=calibration_type)

  def decode_sensor_error(self, record, raw_packet):
    error_type = 'unknown'
    if raw_packet[0] == 0x01:
      error_type = 'end'
    record.update(error_type=error_type)

  def decode_cal_bg_for_gh(self, record, raw_packet):
    amount = lib.BangInt([ (raw_packet[2] & 0b00100000) >> 5, raw_packet[4] ])
    record.update(amount=amount)

  def decode_sensor_cal_factor(self, record, raw_packet):
    factor = lib.BangInt([ raw_packet[4], raw_packet[5] ]) / 1000.0
    record.update(factor=factor)

  def decode_sensor_status(self, record, raw_packet):
    raw_status_type = (raw_packet[2] & 0b01100000) >> 5
    status_type = 'unknown'
    if raw_status_type   == 0x00:
      status_type = 'off'
    elif raw_status_type == 0x01:
      status_type = 'on'
    elif raw_status_type == 0x02:
      status_type = 'lost'
    record.update(status_type=status_type)

  def decode_sensor_sync(self, record, raw_packet):
    raw_sync_type = (raw_packet[2] & 0b01100000) >> 5
    sync_type = 'unknown'
    if raw_sync_type   == 0x01:
      sync_type = 'new'
    elif raw_sync_type == 0x02:
      sync_type = 'old'
    elif raw_sync_type == 0x03:
      sync_type = 'find'
    record.update(sync_type=sync_type)

  def find_initial_timestamp(self):
    """
    Finds the last sensor timestamp in the page and moves it forward by
    5 minutes * number of relative records that occur after. This is a
    way for the relative records in the page that don't have a reference
    to use the timestamp before them. If we didn't do this, we'd have to
    write a history page timestamp every time we want to read the
    current page, which would fill up the glucose history table very
    quickly.

    If the last sensor timestamp is a 'gap' record or it encounters a
    non-relative record other than 0x13 (filler?) or 0x01 (data end)
    before finding the timestamp, returns None
    """
    stream = self.stream_from_data(self.data)
    offset_count = 0

    for B in iter(lambda: stream.read(1), ""):
      B = bytearray(B)
      record = self.decode_record(B[0], stream, None)
      if record['name'] == 'SensorTimestamp' and not record['timestamp_type'] == 'gap':
        timestamp = parser.parse(record['date'])
        return timestamp + relativedelta(minutes=5*offset_count)
      elif self.is_relative_record(record):
        offset_count = offset_count + 1
      elif not (record['name'] == 'DataEnd' or record['name'] == '19-Something'):
        return None

  def byte_to_str (self, byte_array):
    # convert byte array to a string
    hex_bytes = []
    for i in range(0, len(byte_array)):
      hex_bytes.append('{0:02x}'.format(byte_array[i]))
    return '-'.join(hex_bytes)

  def skip_null_bytes (self, data):
    i = 0
    while data[i] == 0x00:
      i = i+1
    return data[i:]

  def stream_from_data(self, data):
    return io.BufferedReader(io.BytesIO(data))

  def check_crc(self, data, expected_crc):
    computed = lib.CRC16CCITT.compute(bytearray(data))
    if lib.BangInt(expected_crc) != computed:
      raise DataTransferCorruptionError("CRC does not match page data")
