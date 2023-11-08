import datetime
from base64 import urlsafe_b64decode, urlsafe_b64encode

from marshmallow import Schema, fields, post_dump, post_load
from marshmallow_enum import EnumField as MarshmallowEnumField


class EpochDateTime(fields.Integer):
    """Use Epoch time for serialized and DateTime deserialized data."""

    def _serialize(self, value, attr, obj, **kwargs):
        """Convert datetime to timestamp for external use."""
        if value is None:
            return None
        try:
            value = value.timestamp() * 1e3  # convert from `s` to `ms`
            return super()._serialize(value, attr, obj, **kwargs)
        except TypeError:
            raise TypeError(f'Expected datetime not "{type(value)}"')

    def _deserialize(self, value, attr, data, **kwargs):
        """Convert timestamp to datetime for internal use.

        :param value: timestamp in milliseconds
        """
        value = super()._deserialize(value, attr, data, **kwargs)
        try:
            return datetime.datetime.fromtimestamp(
                value / 1e3
            )  # convert from `ms` to `s`
        except TypeError:
            raise TypeError(f'Expected timestamp not "{type(value)}"')


class EnumField(MarshmallowEnumField):
    def __init__(
        self,
        enum,
        by_value=False,
        load_by=None,
        dump_by=None,
        error="",
        *args,
        **kwargs,
    ):
        super().__init__(enum, by_value, load_by, dump_by, error, *args, **kwargs)
        self.metadata["enum"] = [e.name for e in enum]


class RoundedFloatField(fields.Field):
    """Add rounding to the Float field."""

    def __init__(self, places=2, *args, **kwargs):
        self.places = places
        super().__init__(*args, **kwargs)

    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return None
        return round(value, self.places)


def snake_to_camel(val):
    components = val.split("_")
    return "".join([components[0].lower()] + [item.title() for item in components[1:]])


class BaseSchema(Schema):
    """Add functionality expected across all schemas."""

    def __init__(self, *args, **kwargs):
        """Serialize/Deserialize fields to/from camelCase.

        https://marshmallow.readthedocs.io/en/stable/quickstart.html#specifying-serialization-deserialization-keys
        """
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if not field.data_key:
                # Allows implementor to override default behaviour
                field.data_key = snake_to_camel(field_name)

    class Meta:
        unknown = "EXCLUDE"


class UpdateSchemaMixin:
    """Add update related fields."""

    updated = EpochDateTime()


class PaginateSchemaMixin:
    """Add fields required for paginated requests."""

    limit = fields.Integer(
        description="Number of records to return, defaults to 100, maximum is 100.",
        example=10,
        missing=100,
    )

    cursor = fields.String(
        description="Cursor used to retrieve next page of data", example="eWEgeWVldA=="
    )

    @post_load
    def post_load(self, data, **kwargs):
        # decode base64-encoded cursor
        if "cursor" in data.keys():
            cursor_bytes = str.encode(data["cursor"])
            data["cursor"] = urlsafe_b64decode(cursor_bytes).decode()

        data["limit"] = min(data["limit"], 100)

        return data


class ResponseMetaSchema(BaseSchema):
    """Add fields required for a paginated response."""

    next_cursor = fields.String(
        description="Cursor used to retrieve next page of data", example="eWEgeWVldA=="
    )

    @post_dump
    def post_dump(self, data, **kwargs):
        if "nextCursor" in data.keys():
            cursor_bytes = str.encode(data["nextCursor"])
            data["nextCursor"] = urlsafe_b64encode(cursor_bytes).decode()

        return data
