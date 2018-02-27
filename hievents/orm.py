"""ORM models."""

from contextlib import suppress
from datetime import datetime
from enum import Enum
from uuid import uuid4

from peewee import PrimaryKeyField, ForeignKeyField, DateField, TimeField, \
    DateTimeField, CharField, TextField, IntegerField, DecimalField

from filedb import mimetype, FileProperty
from functoolsplus import datetimenow
from hinews.exceptions import InvalidCustomer, InvalidTag, InvalidElements
from hinews.proxy import Proxy
from hinews.watermark import watermark
from his.orm import Account
from homeinfo.crm import Address, Customer
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


DATABASE = MySQLDatabase(
    CONFIG['db']['db'], host=CONFIG['db']['host'], user=CONFIG['db']['user'],
    passwd=CONFIG['db']['passwd'], closing=True)


def create_tables(fail_silently=False):
    """Creates all tables."""

    for model in MODELS:
        model.create_table(fail_silently=fail_silently)


@datetimenow
def event_active(now):
    """Returns a peewee expression for active events."""

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
        elif self == Currency.USD:
            return '{} {}'.format(self.value, value)
        elif self == Currency.CHF:
            return '{} {}'.format(self.value, value)
        elif self == Currency.DKK:
            return '{} {}'.format(value, self.value)

        raise NotImplementedError('Cannot format {}.'.format(self.value))


class EventsModel(JSONModel):
    """Basic events database model."""

    class Meta:
        """Configures the database and schema."""
        database = DATABASE
        schema = database.database

    id = PrimaryKeyField()


class Event(EventsModel):
    """An event."""

    author = ForeignKeyField(Account, column_name='author')
    created = DateTimeField(default=datetime.now)
    title = CharField(255)
    subtitle = CharField(255, null=True)
    address = ForeignKeyField(Address, column_name='address')
    begin_date = DateField()
    begin_time = TimeField(null=True)
    end = DateField(null=True)
    active_until = DateField(null=True)

    @classmethod
    def from_dict(cls, author, dictionary, **kwargs):
        """Creates a new event from the provided dictionary."""
        event = super().from_dict(dictionary, **kwargs)
        event.author = author
        return event

    @property
    def editors(self):
        """Yields event editors."""
        return EventEditorProxy(self)

    @property
    def images(self):
        """Yields images of this event."""
        return EventImageProxy(self)

    @property
    def tags(self):
        """Yields tags of this event."""
        return EventTagProxy(self)

    @tags.setter
    def tags(self, tags):
        """Sets the respective tags."""
        for tag in self.tags:
            tag.delete_instance()

        invalid_tags = []

        for tag in tags:
            try:
                self.tags.add(tag)
            except InvalidTag:
                invalid_tags.append(tag)

        if invalid_tags:
            raise InvalidElements(invalid_tags)

    @property
    def customers(self):
        """Yields customers of this event."""
        return EventCustomerProxy(self)

    @customers.setter
    def customers(self, cids):
        """Sets the respective customers."""
        for customer in self.customers:
            customer.delete_instance()

        invalid_customers = []

        for cid in cids:
            try:
                customer = Customer.get(Customer.id == cid)
            except (ValueError, Customer.DoesNotExist):
                invalid_customers.append(cid)
            else:
                self.customers.add(customer)

        if invalid_customers:
            raise InvalidElements(invalid_customers)

    @property
    def sub_events(self):
        """Reutns the respective sub events proxy."""
        return SubEvent.select().where(SubEvent.event == self)

    @property
    def prices(self):
        """Returns the respective prices proxy."""
        return Price.select().where(Price.event == self)

    def to_dict(self, *args, **kwargs):
        """Returns a JSON-ish dictionary."""
        dictionary = super().to_dict(*args, **kwargs)
        dictionary.update({
            'author': self.author.info,
            'address': self.address.to_dict(),
            'editors': [editor.to_dict() for editor in self.editors],
            'images': [image.to_dict() for image in self.images],
            'tags': [tag.to_dict() for tag in self.tags],
            'customers': [customer.to_dict() for customer in self.customers],
            'sub_events': [
                sub_event.to_dict() for sub_event in self.sub_events],
            'prices': [price.to_dict() for price in self.prices]})
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

    def to_dict(self):
        """Returns a JSON-ish dictionary."""
        dictionary = super().to_dict()
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

    def patch(self, dictionary):
        """Patches the image metadata with the respective dictionary."""
        with suppress(KeyError):
            self.source = dictionary['source']

    def to_dict(self):
        """Returns a JSON-compliant integer."""
        dictionary = super().to_dict()
        dictionary['account'] = self.account.info
        dictionary['mimetype'] = mimetype(self._file)
        return dictionary

    def delete_instance(self, recursive=False, delete_nullable=False):
        """Deltes the image."""
        self.data = None    # Delete file.
        return super().delete_instance(
            recursive=recursive, delete_nullable=delete_nullable)


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


class CustomerList(EventsModel):
    """Csutomers enabled for gettings events."""

    class Meta:
        """Sets the table name."""
        table_name = 'customer_list'

    customer = ForeignKeyField(
        Customer, column_name='customer', on_delete='CASCADE',
        on_update='CASCADE')

    def to_dict(self):
        """Returns the respective customer's dict."""
        return self.customer.to_dict(cascade=True)


class Tag(EventsModel):
    """Tags for events."""

    class Meta:
        """Sets the table name."""
        table_name = 'event_tag'

    event = ForeignKeyField(Event, column_name='event', on_delete='CASCADE')
    tag = CharField(255)

    @classmethod
    def add(cls, event, tag, validate=True):
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
        table_name = 'sub_event'

    event = ForeignKeyField(Event, column_name='event', on_delete='CASCADE')
    timestamp = DateTimeField()
    caption = CharField(255, null=True)

    @classmethod
    def add(cls, event, timstamp, caption=None):
        """Adds a new sub-event."""
        sub_event = cls()
        sub_event.event = event
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

    def to_dict(self):
        """Returns a JSON-ish representation of the event customer."""
        return {'id': self.id, 'customer': self.customer.id}


class AccessToken(EventsModel):
    """Customers' access tokens."""

    class Meta:
        """Sets the table name."""
        table_name = 'access_token'

    customer = ForeignKeyField(
        Customer, column_name='customer', on_delete='CASCADE',
        on_update='CASCADE')
    token = CharField(36)   # UUID4

    @classmethod
    def add(cls, customer):
        """Adds an access token for the respective customer."""
        try:
            return cls.get(cls.customer == customer)
        except cls.DoesNotExist:
            access_token = cls()
            access_token.customer = customer
            access_token.token = str(uuid4())
            return access_token


class EventProxy(Proxy):
    """An event-related proxy."""

    def __iter__(self):
        """Yields records related to the respective event."""
        yield from self.model.select().where(self.model.event == self.target)

    def add(self, *args, **kwargs):
        """Adds the respective related model."""
        record = self.model.add(self.target, *args, **kwargs)
        record.save()
        return record

    def delete(self, ident):
        """Deletes the respective instance."""
        try:
            record = self.model.get(
                (self.model.event == self.target) & (self.model.id == ident))
        except self.model.DoesNotExist:
            return False

        return record.delete_instance()


class EventEditorProxy(EventProxy):
    """Proxies event editors."""

    def __init__(self, target):
        """Sets model and target."""
        super().__init__(Editor, target)


class EventImageProxy(EventProxy):
    """Proxies images of events."""

    def __init__(self, target):
        """Sets the model and target."""
        super().__init__(Image, target)


class EventTagProxy(EventProxy):
    """Proxies tags of events."""

    def __init__(self, target):
        """Sets the model and target."""
        super().__init__(Tag, target)

    def delete(self, tag_or_id):
        """Deletes the respective tag."""
        try:
            ident = int(tag_or_id)
        except ValueError:
            selection = self.model.tag == tag_or_id
        else:
            selection = self.model.id == ident

        try:
            event_tag = self.model.get(
                (self.model.event == self.target) & selection)
        except self.model.DoesNotExist:
            return False

        return event_tag.delete_instance()


class EventCustomerProxy(EventProxy):
    """Proxies customers of the respective events."""

    def __init__(self, target):
        """Sets the model and target."""
        super().__init__(EventCustomer, target)

    def __contains__(self, customer):
        """Determines whether the respective
        customer may use the respective event.
        """
        customers = 0

        for customers, event_customer in enumerate(self, start=1):
            if event_customer.customer == customer:
                return True

        return not customers

    def delete(self, customer):
        """Deletes the respective customer from the event."""
        try:
            event_customer = self.model.get(
                (self.model.event == self.target)
                & (self.model.customer == customer))
        except self.model.DoesNotExist:
            return False

        return event_customer.delete_instance()


MODELS = [
    Event, Editor, Image, TagList, CustomerList, Tag, SubEvent,
    Price, EventCustomer, AccessToken]
