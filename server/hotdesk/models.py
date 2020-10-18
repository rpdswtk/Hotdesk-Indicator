"""Model (databate table) definitions."""
from . import db
import datetime
from sqlalchemy import and_


class Desk(db.Model):
    """Desk model."""

    __tablename__ = 'desks'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(6), unique=True)
    # One to many relationship to bookings
    bookings = db.relationship('Booking', backref='desk', lazy='dynamic')

    @property
    def booked(self):
        """Property for is_booked."""
        return self.is_booked()

    def is_booked(self):
        """Find if a desk is currently booked."""
        if any((booking.is_active() for booking in self.bookings)):
            return True
        else:
            return False

    def active_booking(self):
        """Return the active booking for this desk if there is one."""
        for booking in self.bookings:
            if booking.is_active():
                return booking

        return None


class Booking(db.Model):
    """Booking model."""

    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=False)
    from_when = db.Column(db.DateTime, unique=False)
    until_when = db.Column(db.DateTime, unique=False)
    desk_id = db.Column(db.Integer, db.ForeignKey('desks.id'))

    def is_active(self):
        """Find if a booking is currently active."""
        current_time = datetime.datetime.now()
        active = (
            current_time >= self.from_when and current_time < self.until_when
            )
        return active

    def overlap(self, other):
        """
        Test if two bookings overlap.

        :arg other: The booking to test against.
        :type other: :class:`Booking`

        :returns: `True` if the two bookings conflict, `False` otherwise.
        :rtype: bool
        """
        # If other begins after self beings, but also begins before self ends
        if self.from_when <= other.from_when:
            if other.from_when < self.until_when:
                return True

        # Vice versa
        if other.from_when <= self.from_when:
            if self.from_when < other.until_when:
                return True

        return False

    def save(self):
        """Save object to db."""
        db.session.add(self)
        db.session.commit()

    def validate(self):
        """Validate booking."""
        errors = list()

        # Ensure the booking does not overlap with existing bookings
        bookings = Booking.query.filter_by(desk_id=self.desk_id).all()
        if any((self.overlap(other) for other in bookings)):
            errors.append("Your request overlaps with an existing booking.")

        # Ensure the booking ends after it begins
        if self.from_when > self.until_when:
            errors.append("Your request ends after it begins.")

        # Ensure the booking is not for zero time
        if self.from_when == self.until_when:
            errors.append("Your request is for zero time.")

        if len(errors) > 0:
            return errors
        else:
            return None

    @classmethod
    def get_between_interval(cls, start_date, end_date):
        """
        Get bookings between interval.

        :arg start_date: Start date of interval.
        :type start_date: :class:`datetime`

        :arg end_date: End date of interval.
        :type end_date: :class:`datetime`

        :returns: List of Booking objects.
        :rtype: :class`list`
        """
        return cls.query.filter(
            and_(
                cls.from_when.between(start_date, end_date),
                cls.until_when.between(start_date, end_date)
            )
        )
