from marshmallow import Schema, fields

from .accelerometer_schema import AccelerometerSchema
from .gps_schema import GpsSchema
from .aq_schema import AqSchema


class AggregatedDataSchema(Schema):
    accelerometer = fields.Nested(AccelerometerSchema)
    gps = fields.Nested(GpsSchema)
    aq = fields.Nested(AqSchema)
    timestamp = fields.DateTime("iso")
    user_id = fields.Int()
