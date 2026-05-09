from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import types
Base = declarative_base()

class NullToEmptyString(types.TypeDecorator):
    impl = types.String
    def process_result_value(self, value, engine):
        return value if value is not None else ""
