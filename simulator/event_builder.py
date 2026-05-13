#this will build the events that the actual json document gets to send to the Event Hub. 
#this also where all five streaming anomalies get injected based on the probabilities in config.py
import uuid
import random
import asyncio
from datetime import datetime, timezone, timedelta
from typing import Optional
from simulator.price_model import InstrumentState
from simulator.config import (
    DUPLICATE_PROBABILITY,
    LATE_ARRIVAL_PROBABILITY,
    OUT_OF_ORDER_PROBABILITY,
)


def _now_utc() -> str:
    """Returns current UTC time as ISO 8601 string with milliseconds."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def _utc_offset(seconds: int) -> str:
    """Returns a UTC timestamp offset by `seconds` (negative = past)."""
    dt = datetime.now(timezone.utc) + timedelta(seconds=seconds)
    return dt.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


class EventBuilder:
    """
    Builds fully-formed tick event documents ready for Event Hubs.
    Stateful — tracks sequence numbers and last event per symbol
    for duplicate injection.
    """

    def __init__(self, instruments: dict):
        # sequence counter per symbol for monotonic event_id generation
        self._sequence: dict[str, int] = {s: 0 for s in instruments}

        # last built event per symbol used for duplicate injection
        self._last_event: dict[str, Optional[dict]] = {s: None for s in instruments}

    # Public API now

    def build(
        self,
        symbol: str,
        meta: dict,
        state: InstrumentState,
    ) -> tuple[dict, float]:
        """
        Builds one tick event for the given symbol.

        Returns:
            (event_dict, delay_seconds)
            delay_seconds > 0 means the caller must sleep before sending —
            this simulates late arrival without blocking the build step.
        """
        # injecting the duplicate if duplicate, return the previous event as-is
        if (
            self._last_event[symbol] is not None
            and random.random() < DUPLICATE_PROBABILITY
        ):
            dupe = dict(self._last_event[symbol])
            dupe["is_duplicate"] = True
            return dupe, 0.0

        # advance sequence 
        self._sequence[symbol] += 1
        seq = self._sequence[symbol]

        # gets the next price tick from GBM model 
        price, bid, ask = state.next_tick()

        #determine the side probabilistically
        side = "BUY" if random.random() < 0.52 else "SELL"

        #  quantity, this is like lot sizes per asset class
        if meta["asset_class"] == "EQUITY":
            #Since the JSE minimum lot is typically 1 share and institutions trade with 100s
            quantity = random.choice([100, 200, 500, 1000, 2000, 5000])
        else:
            #Crypto is traded in fractional units such as integer lol you cant buy one Bitcoin unless you are rich
            #e.g. 500000 = 0.5 BTC
            quantity = random.choice([50_000, 100_000, 250_000, 500_000, 1_000_000])

        #Event time
        is_out_of_order = random.random() < OUT_OF_ORDER_PROBABILITY
        if is_out_of_order:
            # backdate by 30 seconds to simulate out-of-order arrival
            event_ts = _utc_offset(-30)
        else:
            event_ts = _now_utc()

        # late arrival, will be sent 35s after build  
        is_late = random.random() < LATE_ARRIVAL_PROBABILITY
        delay   = 35.0 if is_late else 0.0

        #assemble event document 
        event = {
            "event_id":    str(uuid.uuid4()),
            "sequence_num": seq,
            "symbol":      symbol,
            "asset_class": meta["asset_class"],
            "exchange":    meta["exchange"],
            "price":       price,
            "quantity":    quantity,
            "side":        side,
            "bid":         bid,
            "ask":         ask,
            "spread":      ask - bid,
            "event_ts":    event_ts,
            "ingestion_ts": _now_utc(),   # set at build time not send time 
            "is_duplicate": False,
            "is_late":      is_late,
            "is_out_of_order": is_out_of_order,
            "realised_vol": state.current_volatility(),
        }

        #store as last event for potential future duplicate
        self._last_event[symbol] = event
        return event, delay
