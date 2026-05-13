# simulator/base_producer.py
import asyncio
import json
import logging
import random
import time
from azure.eventhub.aio import EventHubProducerClient
from azure.eventhub import EventData
from simulator.price_model import build_instrument_states
from simulator.event_builder import EventBuilder
from simulator.config import (
    BURST_INTERVAL_SECONDS,
    BURST_EVENT_COUNT,
    BURST_SLEEP_SECONDS,
    MIN_SLEEP_SECONDS,
    MAX_SLEEP_SECONDS,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s"
)


class BaseProducer:
    """
    Async Event Hub producer for a given set of instruments.
    Handles normal throughput, burst injection, and late arrival delays.
    Subclass this for JSE and Crypto — do not instantiate directly.
    """

    def __init__(
        self,
        name: str,
        connection_string: str,
        eventhub_name: str,
        instruments: dict,
    ):
        self.name              = name
        self.connection_string = connection_string
        self.eventhub_name     = eventhub_name
        self.instruments       = instruments
        self.logger            = logging.getLogger(name)

        # initialise GBM states and event builder once at startup
        self.states  = build_instrument_states(instruments)
        self.builder = EventBuilder(instruments)

        # metrics — logged periodically, useful for Criterion 7
        self._sent_count      = 0
        self._late_count      = 0
        self._duplicate_count = 0
        self._error_count     = 0
        self._start_time      = None

    #Internal helpers 

    async def _send_event(
        self,
        producer: EventHubProducerClient,
        symbol: str,
    ) -> None:
        """Builds one event and sends it. Handles late arrival delay."""
        meta        = self.instruments[symbol]
        state       = self.states[symbol]
        event, delay = self.builder.build(symbol, meta, state)

        # late arrival, sleep before sending, simulating network delay
        if delay > 0:
            self._late_count += 1
            self.logger.info(f"[LATE] {symbol} — delaying {delay}s before send")
            await asyncio.sleep(delay)

        if event.get("is_duplicate"):
            self._duplicate_count += 1
            self.logger.info(f"[DUPE] {symbol} — resending event_id={event['event_id']}")

        try:
            batch = await producer.create_batch(partition_key=symbol)
            batch.add(EventData(json.dumps(event)))
            await producer.send_batch(batch)
            self._sent_count += 1

            self.logger.debug(
                f"[SENT] {symbol} | price={event['price']} "
                f"side={event['side']} seq={event['sequence_num']}"
            )

        except Exception as e:
            self._error_count += 1
            self.logger.error(f"[ERROR] Failed to send {symbol}: {e}")

    async def _burst(self, producer: EventHubProducerClient) -> None:
        """
        Sends BURST_EVENT_COUNT events rapidly across random symbols.
        Simulates market open or news-driven volume spike.
        """
        symbols = list(self.instruments.keys())
        self.logger.info(f"[BURST] Injecting {BURST_EVENT_COUNT} events rapidly")

        for _ in range(BURST_EVENT_COUNT):
            symbol = random.choice(symbols)
            await self._send_event(producer, symbol)
            await asyncio.sleep(BURST_SLEEP_SECONDS)

    def _log_metrics(self) -> None:
        """Logs throughput and anomaly injection stats."""
        elapsed = time.time() - self._start_time
        tps     = self._sent_count / elapsed if elapsed > 0 else 0
        self.logger.info(
            f"[METRICS] {self.name} | "
            f"sent={self._sent_count} | "
            f"tps={tps:.2f} | "
            f"late={self._late_count} | "
            f"dupes={self._duplicate_count} | "
            f"errors={self._error_count} | "
            f"elapsed={elapsed:.0f}s"
        )

    # Main run loop 

    async def run(self) -> None:
        """
        Main producer loop. Runs indefinitely until KeyboardInterrupt.
        Cycles through all instruments, sending one tick each pass.
        Injects a burst every BURST_INTERVAL_SECONDS.
        Logs metrics every 60 seconds.
        """
        self.logger.info(
            f"[START] {self.name} — "
            f"{len(self.instruments)} instruments → {self.eventhub_name}"
        )
        self._start_time      = time.time()
        last_burst_time       = time.time()
        last_metrics_time     = time.time()

        async with EventHubProducerClient.from_connection_string(
            conn_str=self.connection_string,
            eventhub_name=self.eventhub_name,
        ) as producer:

            while True:
                try:
                    # normal tick cycle 
                    # one tick per instrument per cycle
                    for symbol in self.instruments:
                        await self._send_event(producer, symbol)
                        sleep = random.uniform(MIN_SLEEP_SECONDS, MAX_SLEEP_SECONDS)
                        await asyncio.sleep(sleep)

                    # burst injection 
                    if time.time() - last_burst_time >= BURST_INTERVAL_SECONDS:
                        await self._burst(producer)
                        last_burst_time = time.time()

                    # metrics logging
                    if time.time() - last_metrics_time >= 60:
                        self._log_metrics()
                        last_metrics_time = time.time()

                except KeyboardInterrupt:
                    self.logger.info(f"[STOP] {self.name} shutting down")
                    self._log_metrics()
                    break

                except Exception as e:
                    self._error_count += 1
                    self.logger.error(f"[LOOP ERROR] {self.name}: {e}")
                    await asyncio.sleep(2)