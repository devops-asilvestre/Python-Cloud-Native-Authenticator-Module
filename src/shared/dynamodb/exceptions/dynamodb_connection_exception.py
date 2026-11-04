"""DynamoDB connectivity exception."""

from shared.dynamodb.exceptions.dynamodb_exception import DynamoDbException


class DynamoDbConnectionException(DynamoDbException):
    """Raised when DynamoDB cannot be reached or accessed."""
