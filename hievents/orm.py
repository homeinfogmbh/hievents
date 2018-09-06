"""ORM models."""

from datetime import datetime
from enum import Enum
from uuid import uuid4

from peewee import ForeignKeyField, DateField, DateTimeField, CharField, \
    TextField, IntegerField, DecimalField, UUIDField

from filedb import mimetype, FileProperty
from hinews.exceptions import InvalidCustomer, InvalidTag
from hinews.watermark import watermark
from his.orm import Account
from mdb import Address, Customer
from peeweeplus import MySQLDatabase, JSONModel, EnumField

from hievents.config import CONFIG

__all__ = [
    'create_tables',
    'Event',
    'Editor',
    'Image',
    'TagList',
    'CustomerList',
    'Tag',
    'SubEvent',
    'Price',
    'EventCustomer',
    'AccessToken',
    'MODELS']


DATABASE = MySQLDatabase.from_config(CONFIG['db'])


def create_tables(fail_silently=False):
    """Creates all tables."""

    for model in MODELS:
        model.create_table(fail_silently=fail_silently)


def event_active():
    """Returns a peewee expression for active events."""

    now = datetime.now()
    return (
        ((Event.active_from >> None) | (Event.active_from <= now))
        & ((Event.active_until >> None) | (Event.active_until >= now)))


class Currency(Enum):
    """Available currencies."""

    EUR = '€'
    USD = '$'
    CHF = 'Fr.'
    DKK = 'kr.'

    def format(self, value):
        """Formats the respective currency value."""
        if self == Currency.EUR:
            return '{} {}'.format(value, self.value)

        if self == Currency.USD:
            return '{} {}'.format(self.value, value)

        if self == Currency.CHF:
            return '{} {}'.format(self.value, value)

        if self == Currency.DKK:
            return '{} {}'.format(value, self.value)

        raise NotImplementedError('Cannot format {}.'.format(self.value))


class EventsModel(JSONModel):
    """Basic events database model."""

    class Meta:
        """Configures the database and schema."""
        database = DATABASE
        schema = database.database


class Event(EventsModel):
    """An event."""

    author = ForeignKeyField(Account, column_name='author')
    created = DateTimeField(default=datetime.now)
    title = CharField(255)
    subtitle = CharField(255, null=True)
    address = ForeignKeyField(Address, column_name='address')
    begin = DateField()
    end = DateField(null=True)
    active_until = DateField(null=True)

    @classmethod
    def from_json(cls, author, dictionary, **kwargs):
        """Creates a new event from the provided dictionary."""
        event = super().from_json(dictionary, **kwargs)
        event.author = author
        return event

    @property
    def editors(self):
        """Yields event editors."""
        return Editor.select().where(Editor.event == self)

    @property
    def images(self):
        """Yields images of this event."""
        return Image.select().where(Image.event == self)

    @property
    def tags(self):
        """Yields tags of this event."""
        return Tag.select().where(Tag.event == self)

    @property
    def customers(self):
        """Yields customers of this event."""
        return EventCustomer.select().where(EventCustomer.event == self)

    @property
    def sub_events(self):
        """Yield the respective sub-events."""
        return SubEvent.select().where(SubEvent.event == self)

    @property
    def prices(self):
        """Yield the respective prices."""
        return Price.select().where(Price.event == self)

    def to_json(self, *args, **kwargs):
        """Returns a JSON-ish dictionary."""
        dictionary = super().to_json(*args, **kwargs)
        dictionary.update({
            'author': self.author.info,
            'address': self.address.to_json(),
            'editors': [editor.id for editor in self.editors],
            'images': [image.id for image in self.images],
            'tags': [tag.id for tag in self.tags],
            'customers': [customer.id for customer in self.customers],
            'sub_events': [sub_event.id for sub_event in self.sub_events],
            'prices': [price.id for price in self.prices]})
        return dictionary

    def delete_instance(self, recursive=False, delete_nullable=False):
        """Deletes the event."""
        # Manually delete all referencing images to ensure
        # deletion of the respective filedb entries.
        for image in self.images:
            image.delete_instance()

        return super().delete_instance(
            recursive=recursive, delete_nullable=delete_nullable)


class Editor(EventsModel):
    """An event's editor."""

    class Meta:
        """Sets the table name."""
        table_name = 'event_editor'

    event = ForeignKeyField(Event, column_name='event', on_delete='CASCADE')
    account = ForeignKeyField(
        Account, column_name='account', on_delete='CASCADE')
    timestamp = DateTimeField(default=datetime.now)

    @classmethod
    def add(cls, event, account):
        """Adds a new author record to the respective event."""
        event_editor = cls()
        event_editor.event = event
        event_editor.account = account
        return event_editor

    def to_json(self):
        """Returns a JSON-ish dictionary."""
        dictionary = super().to_json()
        dictionary['account'] = self.account.info
        return dictionary


class Image(EventsModel):
    """An image of an event."""

    class Meta:
        """Sets the table name."""
        table_name = 'image'

    event = ForeignKeyField(Event, column_name='event', on_delete='CASCADE')
    account = ForeignKeyField(
        Account, column_name='account', on_delete='CASCADE')
    _file = IntegerField(column_name='file')
    uploaded = DateTimeField(default=datetime.now)
    source = TextField(null=True)
    data = FileProperty(_file)

    @classmethod
    def add(cls, event, data, metadata, account):
        """Adds the respective image data to the event."""
        event_image = cls()
        event_image.event = event
        event_image.account = account
        event_image.data = data
        event_image.source = metadata['source']
        return event_image

    @property
    def oneliner(self):
        """Returns the source text as a one-liner."""
        return ' '.join(self.source.split('\n'))

    @property
    def watermarked(self):
        """Returns a watermarked image."""
        return watermark(self.data, 'Quelle: {}'.format(self.oneliner))

    def patch_json(self, dictionary):
        """Patches the image metadata with the respective dictionary."""
        return super().patch_json(
            dictionary, skip=('uploaded',), fk_fields=False)

    def to_json(self):
        """Returns a JSON-compliant integer."""
        dictionary = super().to_json()
        dictionary['account'] = self.account.info
        dictionary['mimetype'] = mimetype(self._file)
        return dictionary

    def delete_instance(self, recursive=False, delete_nullable=False):
        """Deltes the image."""
        self.data = None    # Delete file.
        return super().delete_instance(
            recursive=recursive, delete_nullable=delete_nullable)


class Tag(EventsModel):
    """Tags for events."""

    class Meta:
        """Sets the table name."""
        table_name = 'event_tag'

    event = ForeignKeyField(Event, column_name='event', on_delete='CASCADE')
    tag = CharField(255)

    @classmethod
    def from_text(cls, event, tag, validate=True):
        """Adds a new tag to the event."""
        if validate:
            try:
                TagList.get(TagList.tag == tag)
            except TagList.DoesNotExist:
                raise InvalidTag(tag)

        try:
            return cls.get((cls.event == event) & (cls.tag == tag))
        except cls.DoesNotExist:
            event_tag = cls()
            event_tag.event = event
            event_tag.tag = tag
            return event_tag


class SubEvent(EventsModel):
    """A sub-event."""

    class Meta:
        """Set table name."""
        table_name = 'sub_event'

    event = ForeignKeyField(Event, column_name='event', on_delete='CASCADE')
    timestamp = DateTimeField()
    caption = CharField(255, null=True)

    @classmethod
    def add(cls, event, timestamp, caption=None):
        """Adds a new sub-event."""
        sub_event = cls()
        sub_event.event = event
        sub_event.timestamp = timestamp
        sub_event.caption = caption
        return sub_event


class Price(EventsModel):
    """Price of an event."""

    event = ForeignKeyField(Event, column_name='event', on_delete='CASCADE')
    value = DecimalField(6, 2)
    currency = EnumField(Currency, default=Currency.EUR)
    caption = CharField(255, null=True)

    @classmethod
    def add(cls, event, value, currency=Currency.EUR, caption=None):
        """Adds a new price."""
        price = cls()
        price.event = event
        price.value = value
        price.currency = currency
        price.caption = caption
        return price


class EventCustomer(EventsModel):
    """Customer <> Event mappings."""

    class Meta:
        """Sets the table name."""
        table_name = 'event_customer'

    event = ForeignKeyField(Event, column_name='event', on_delete='CASCADE')
    customer = ForeignKeyField(
        Customer, column_name='customer', on_delete='CASCADE')

    @classmethod
    def add(cls, event, customer):
        """Adds the respective customer to the event."""
        try:
            CustomerList.get(CustomerList.customer == customer)
        except CustomerList.DoesNotExist:
            raise InvalidCustomer(customer)

        try:
            return cls.get(
                (cls.event == event) & (cls.customer == customer))
        except cls.DoesNotExist:
            event_customer = cls()
            event_customer.event = event
            event_customer.customer = customer
            return event_customer

    def to_json(self):
        """Returns a JSON-ish representation of the event customer."""
        return {'id': self.id, 'customer': self.customer.id}


class CustomerList(EventsModel):
    """Csutomers enabled for gettings events."""

    class Meta:
        """Sets the table name."""
        table_name = 'customer_list'

    customer = ForeignKeyField(
        Customer, column_name='customer', on_delete='CASCADE',
        on_update='CASCADE')

    def to_json(self):
        """Returns the respective customer's dict."""
        return self.customer.to_json(company=True)


class TagList(EventsModel):
    """Available tags."""

    class Meta:
        """Sets the table name."""
        table_name = 'tag_list'

    tag = CharField(255)

    @classmethod
    def add(cls, tag):
        """Adds the respective tag."""
        try:
            return cls.get(cls.tag == tag)
        except cls.DoesNotExist:
            tag_ = cls()
            tag_.tag = tag
            return tag_


class AccessToken(EventsModel):
    """Customers' access tokens."""

    class Meta:
        """Sets the table name."""
        table_name = 'access_token'

    customer = ForeignKeyField(
        Customer, column_name='customer', on_delete='CASCADE',
        on_update='CASCADE')
    token = UUIDField(default=uuid4)

    @classmethod
    def add(cls, customer):
        """Adds an access token for the respective customer."""
        try:
            return cls.get(cls.customer == customer)
        except cls.DoesNotExist:
            access_token = cls()
            access_token.customer = customer
            return access_token


MODELS = [
    Event, Editor, Image, TagList, CustomerList, Tag, SubEvent,
    Price, EventCustomer, AccessToken]
