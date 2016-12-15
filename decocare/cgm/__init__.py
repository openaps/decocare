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
from datetime import datetime
from dateutil.relativedelta import relativedelta
from dateutil import parser

from decocare import lib
from decocare.records import times
from decocare.errors import DataTransferCorruptionError
from pprint import pprint

###################
#
# Time parser
# TODO: document
# TODO: tests, ideally ones showing bits flip over
###################

def parse_minutes (one):
  minute = (one & 0b111111 )
  return minute

def parse_hours (one):
  return (one & 0x1F )

def parse_day (one):
  return one & 0x1F

def parse_months (first_byte, second_byte):
  first_two_bits  = first_byte  >> 6
  second_two_bits = second_byte >> 6
  return (first_two_bits << 2) + second_two_bits


def parse_date (data, unmask=False, strict=False, minute_specific=False):
  """
  Some dates are formatted/stored down to the second (Sensor CalBGForPH) while
    others are stored down to the minute (CGM SensorTimestamp dates).
  """
  data = data[:]
  seconds = 0
  minutes = 0
  hours   = 0

  year    = times.parse_years(data[0])
  day     = parse_day(data[1])
  minutes = parse_minutes(data[2])
  hours   = parse_hours(data[3])
  month   = parse_months(data[3], data[2])

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

  @classmethod
  def Data (klass, data, **kwds):
    stream = io.BufferedReader(io.BytesIO(data))
    return klass(stream, **kwds)

  def __init__ (self, stream, larger=False):
    raw = bytearray(stream.read(1024))
    data, crc = raw[0:1022], raw[1022:]
    computed = lib.CRC16CCITT.compute(bytearray(data))
    self.larger = larger
    if lib.BangInt(crc) != computed:
      raise DataTransferCorruptionError("CRC does not match page data")

    data.reverse()
    # self.data = data
    self.data = self.eat_nulls(data)
    # self.stream = io.BufferedReader(io.BytesIO(self.data))

  def eat_nulls (self, data):
    i = 0
    while data[i] == 0x00:
      i = i+1
    return data[i:]

  def stream_from_data(self, data):
    return io.BufferedReader(io.BytesIO(data))

  def decode (self):
    records = []
    timestamp = None
    stream = self.stream_from_data(self.data)

    for B in iter(lambda: stream.read(1), ""):
      B = bytearray(B)
      record = self.decode_record(B[0], stream, timestamp)
      if record['name'] == 'SensorTimestamp':
        timestamp = parser.parse(record['date'])
      elif 'date_type' in record and record['date_type'] == 'relative' and timestamp:
        timestamp = timestamp + relativedelta(minutes=-5)
      records.append(record)

    records.reverse()
    self.records = records
    return self.records

  def decode_record (self, op, stream, timestamp):
    """
    return a partially filled in packet/opcode
     info: name, packet size, date_type, op
     some info will be added later when the record is parsed
    """
    # TODO: would it be possible to turn these into classes which know hwo
    # to decode time and describe themselves to PagedData?
    # that way we can write tests for each type individually and tests for
    # the thing as a whole easily.
    records = {
      0x01: dict(name='DataEnd',packet_size=0,date_type='none',op='0x01'),
      0x02: dict(name='SensorWeakSignal',packet_size=0,date_type='relative',op='0x02'),
      0x03: dict(name='SensorCal',packet_size=1,date_type='relative',op='0x03'),
      0x04: dict(name='SensorPacket',packet_size=1,date_type='relative',op='0x04'),
      0x05: dict(name='SensorError',packet_size=1,date_type='relative',op='0x05'),
      0x06: dict(name='SensorDataLow',packet_size=0,date_type='relative',op='0x06'),
      0x07: dict(name='SensorDataHigh',packet_size=1,date_type='relative',op='0x07'),
      0x08: dict(name='SensorTimestamp',packet_size=4,date_type='reference',op='0x08'),
      0x0a: dict(name='BatteryChange',packet_size=4,date_type='minSpecific',op='0x0a'),
      0x0b: dict(name='SensorStatus',packet_size=4,date_type='minSpecific',op='0x0b'),
      0x0c: dict(name='DateTimeChange',packet_size=4,date_type='minSpecific',op='0x0c'),
      0x0d: dict(name='SensorSync',packet_size=4,date_type='minSpecific',op='0x0d'),
      0x0e: dict(name='CalBGForGH',packet_size=5,date_type='minSpecific',op='0x0e'),
      0x0f: dict(name='SensorCalFactor',packet_size=6,date_type='minSpecific',op='0x0f'),
      0x10: dict(name='10-Something',packet_size=7,date_type='minSpecific',op='0x10'),
    }
    if self.larger:
      # record[08][]
      pass

    if op > 0 and op < 20:
      record = records.get(op, None)
      if record is None:
        record = dict(name='Could Not Decode',packet_size=0,op=op)
    else:
      record = dict(name='GlucoseSensorData',packet_size=0,date_type='relative',op=op)
      record.update(sgv=(int(op) * 2))

    record['_tell'] = stream.tell( )

    # read packet if needed
    if not record is None and record['packet_size'] > 0:
      raw_packet = bytearray(stream.read(record['packet_size']))

    # SensorTimestamp serves as a reference timestamp for relative events
    if record['name'] == 'SensorTimestamp':
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

      date, body = raw_packet[:4], raw_packet[4:]
      date.reverse()
      date = parse_date(date)
      if date:
        record.update(date=date.isoformat())
      else:
        print "@@@", self.stream.tell( )
        pprint(dict(raw=hexlify(raw_packet)))
        pprint(dict(date=hexlify(date or bytearray( ))))
        pprint(dict(body=hexlify(body)))

    elif 'date_type' in record and record['date_type'] == 'relative':
      if timestamp:
        record.update(date=timestamp.isoformat())

      if record['name'] == 'SensorCal':
        record.update(raw=self.byte_to_str(raw_packet))
        calibration_type = 'unknown'
        if raw_packet[0] == 0x00:
          calibration_type = 'meter_bg_now'
        if raw_packet[0] == 0x01:
          calibration_type = 'waiting'
        if raw_packet[0] == 0x02:
          calibration_type = 'cal_error'
        record.update(calibration_type=calibration_type)

      if record['name'] == 'SensorError':
        error_type = 'unknown'
        if raw_packet[0] == 0x01:
          error_type = 'end'
        record.update(error_type=error_type)

    # independent record => parse and add to records list
    elif 'date_type' in record and record['date_type'] == 'minSpecific':
      record.update(raw=self.byte_to_str(raw_packet))
      date, body = raw_packet[:4], raw_packet[4:]
      date.reverse()
      date = parse_date(date)
      if date is not None:
        record.update(date=date.isoformat())
      else:
        record.update(_date=str(raw_packet[:4]).encode('hex'))
      record.update(body=self.byte_to_str(body))

      # Update cal amount
      if record['name'] == 'CalBGForGH':
        amount = lib.BangInt([ (raw_packet[2] & 0b00100000) >> 5, body[0] ])
        record.update(body=self.byte_to_str(body))
        record.update(amount=amount)

      # Update sensor cal factor
      if record['name'] == 'SensorCalFactor':
        factor = lib.BangInt([ body[0], body[1] ]) / 1000.0
        record.update(factor=factor)

      #Update sensor status type
      if record['name'] == 'SensorStatus':
        raw_status_type = (raw_packet[2] & 0b01100000) >> 5
        status_type = 'unknown'
        if raw_status_type   == 0x00:
          status_type = 'off'
        elif raw_status_type == 0x01:
          status_type = 'on'
        elif raw_status_type == 0x02:
          status_type = 'lost'
        record.update(status_type=status_type)

      #Update sensor sync type
      if record['name'] == 'SensorSync':
        raw_sync_type = (raw_packet[2] & 0b01100000) >> 5
        sync_type = 'unknown'
        if raw_sync_type   == 0x01:
          sync_type = 'new'
        elif raw_sync_type == 0x02:
          sync_type = 'old'
        elif raw_sync_type == 0x03:
          sync_type = 'find'
        record.update(sync_type=sync_type)

      #Update origin type
      if record['name'] == 'CalBGForGH':
        raw_origin_type = (raw_packet[2] & 0b01100000) >> 5
        origin_type = 'unknown'
        if raw_origin_type == 0x00:
          origin_type = 'rf'
        record.update(origin_type=origin_type)

    return record

  def byte_to_str (self, byte_array):
    # convert byte array to a string
    hex_bytes = []
    for i in range(0, len(byte_array)):
      hex_bytes.append('{0:02x}'.format(byte_array[i]))
    return '-'.join(hex_bytes)


