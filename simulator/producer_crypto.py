# simulator/producer_crypto.py
from simulator.base_producer import BaseProducer
from simulator.config import (
    CRYPTO_CONNECTION_STRING,
    CRYPTO_EVENTHUB_NAME,
    CRYPTO_INSTRUMENTS,
)


class CryptoProducer(BaseProducer):
    def __init__(self):
        super().__init__(
            name              = "CryptoProducer",
            connection_string = CRYPTO_CONNECTION_STRING,
            eventhub_name     = CRYPTO_EVENTHUB_NAME,
            instruments       = CRYPTO_INSTRUMENTS,
        )