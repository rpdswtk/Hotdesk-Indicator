"""RESTful API resources."""
from . import api
from ..models import Desk, Booking
from .schemas import DeskSchema, BookingSchema
from flask_restful import Resource
from flask import request, abort
from datetime import datetime

desk_schema = DeskSchema(many=True)
booking_schema = BookingSchema()
bookings_schema = BookingSchema(many=True)

DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S"


@api.resource('/api/desk_status/<string:desk_id>')
class DeskStatus(Resource):
    """Desk status RESTful resource."""

    def get(self, desk_id):
        """
        Handle a get request to the DeskStatus resource.

        This returns the current status of a desk.

        :arg str desk_id: The unique identifier of the desk whose status should
            be returned.

        :returns: The status of desk `desk_id`.
        :rtype: dict
        """
        desk = Desk.query.get_or_404(desk_id)
        if desk.is_booked():
            booked = True
            active_booking = desk.active_booking()
            until = active_booking.until_when.strftime("%H:%M")
            by = active_booking.name
        else:
            booked = False
            until = "n/a"
            by = "n/a"

        return {
            "name": desk.name,
            "booked": booked,
            "by": by,
            "until": until
            }


@api.resource('/api/desk_status')
class DesksList(Resource):
    """Desk status list RESTful resource."""

    def get(self):
        """
        Handle a get request to the DesksList resource.

        This returns all desks with booked status.
        """
        desks = Desk.query.all()
        return desk_schema.dump(desks)


@api.resource('/api/booking')
class BookingResource(Resource):
    """Booking RESTful resource."""

    def get(self):
        """Handle a get request to get bookings between a given interval."""
        start_date = datetime.strptime(
            request.args['start_date'],
            DATETIME_FORMAT
        )
        end_date = datetime.strptime(
            request.args['end_date'],
            DATETIME_FORMAT
        )
        return bookings_schema.dump(
            Booking.get_between_interval(start_date, end_date)
        )

    def post(self):
        """Handle a post request to create new booking."""
        errors = booking_schema.validate(request.args)
        if errors:
            abort(400, str(errors))

        from_when = datetime.strptime(
            request.args['from_when'],
            DATETIME_FORMAT
        )

        until_when = datetime.strptime(
            request.args['until_when'],
            DATETIME_FORMAT
        )

        booking = Booking(
            name=request.args["name"],
            desk_id=request.args["desk_id"],
            from_when=from_when,
            until_when=until_when
        )
        errors = booking.validate()

        if errors:
            abort(400, str(errors))

        booking.save()

        return 201, {"msg": "Booking created"}
