"""Marshmallow schemas."""
from .. import ma


class DeskSchema(ma.Schema):
    """Marshmallow schema definition for Desk model."""

    class Meta:
        """Meta class for schema."""

        fields = ('id', 'name', 'booked')
