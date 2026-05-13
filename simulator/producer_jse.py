# simulator/producer_jse.py
from simulator.base_producer import BaseProducer
from simulator.config import (
    JSE_CONNECTION_STRING,
    JSE_EVENTHUB_NAME,
    JSE_INSTRUMENTS,
)


class JSEProducer(BaseProducer):
    def __init__(self):
        super().__init__(
            name              = "JSEProducer",
            connection_string = JSE_CONNECTION_STRING,
            eventhub_name     = JSE_EVENTHUB_NAME,
            instruments       = JSE_INSTRUMENTS,
        )