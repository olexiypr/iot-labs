from marshmallow import Schema, fields


class TrafficLight(Schema):
    traffic_light_id = fields.Int()
    timestamp = fields.DateTime("iso")
    cars_waiting = fields.Int()
    longitude = fields.Number()
    latitude = fields.Number()
