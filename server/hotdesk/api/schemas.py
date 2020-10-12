"""Marshmallow schemas."""
from .. import ma
from marshmallow import fields as ma_fields


class DeskSchema(ma.Schema):
    """Marshmallow schema definition for Desk model."""

    class Meta:
        """Meta class for schema."""

        fields = ('id', 'name', 'booked')


class BookingSchema(ma.Schema):
    """Marshmallow schema definition for Booking model."""

    id = ma_fields.Integer()
    name = ma_fields.Str(required=True)
    from_when = ma_fields.DateTime(required=True)
    until_when = ma_fields.DateTime(required=True)
    desk_id = ma.Integer(required=True)
