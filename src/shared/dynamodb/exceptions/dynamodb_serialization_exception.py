"""DynamoDB serialization exception."""

from shared.dynamodb.exceptions.dynamodb_exception import DynamoDbException


class DynamoDbSerializationException(DynamoDbException):
    """Raised when an item cannot be converted to/from DynamoDB types."""
