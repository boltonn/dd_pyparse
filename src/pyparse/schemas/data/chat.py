from pyparse.schemas.enums import DataType
from pyparse.schemas.data.parents.message import Message


class Chat(Message):
    data_type = DataType.chat
