from marshmallow import Schema, fields


class AqSchema(Schema):
    co2_level = fields.Int()
    temperature = fields.Float()
    pm2_5 = fields.Int()
    pm10 = fields.Int()