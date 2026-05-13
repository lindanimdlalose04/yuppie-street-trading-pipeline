# simulator/main.py
import asyncio
from simulator.producer_jse import JSEProducer
from simulator.producer_crypto import CryptoProducer


async def main():
    """
    Runs both producers concurrently as async tasks.
    Both connect to their own Event Hub simultaneously.
    Ctrl+C shuts both down cleanly.
    """
    jse_producer    = JSEProducer()
    crypto_producer = CryptoProducer()

    await asyncio.gather(
        jse_producer.run(),
        crypto_producer.run(),
    )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] Both producers stopped.")