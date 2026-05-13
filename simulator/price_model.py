import numpy as np
from dataclasses import dataclass, field
from typing import Tuple
#this will give me the numbers 

# dt represents one tick as a fraction of a trading year
# 252 trading days × 390 minutes per day = 98,280 ticks per year
# Using per-minute ticks as our base unit
TRADING_TICKS_PER_YEAR = 98_280
DT = 1 / TRADING_TICKS_PER_YEAR


@dataclass
class InstrumentState:
    """
    Holds the live price state for a single instrument.
    Mutated on every tick — this is what makes it stateful.
    """
    symbol:       str
    current_price: int          # stored in cents/minor units — never float
    volatility:   float         # annualised from config
    drift:        float = 0.05  # annualised — slight upward market bias

    # rolling window of last 20 prices for spread calculation
    price_history: list = field(default_factory=list)

    def next_tick(self) -> Tuple[int, int, int]:
        """
        Advances price by one tick using GBM.
        Returns: (new_price, bid, ask) all in integer minor units
        """
        #   GBM core 
        Z             = np.random.standard_normal()
        shock         = (self.drift - 0.5 * self.volatility ** 2) * DT \
                        + self.volatility * np.sqrt(DT) * Z
        new_price_f   = self.current_price * np.exp(shock)

        # floor at 1 cent — price can never go negative or zero
        new_price     = max(1, int(round(new_price_f)))
        self.current_price = new_price

        # rolling price history 
        self.price_history.append(new_price)
        if len(self.price_history) > 20:
            self.price_history.pop(0)

        #bid/ask spread 
        # spread is proportional to volatility — more volatile = wider spread
        # base spread: 0.05% of price, scaled by volatility
        spread_bps    = max(1, int(self.volatility * 1000))  # basis points
        half_spread   = max(1, int(new_price * spread_bps / 20_000))
        bid           = new_price - half_spread
        ask           = new_price + half_spread

        return new_price, bid, ask

    def current_volatility(self) -> float:
        """
        Realised volatility from recent price history.
        Used by Stream Analytics anomaly detection as a benchmark.
        Returns annualised volatility as a float.
        """
        if len(self.price_history) < 5:
            return self.volatility

        prices  = np.array(self.price_history, dtype=float)
        log_ret = np.diff(np.log(prices))
        realised = float(np.std(log_ret) * np.sqrt(TRADING_TICKS_PER_YEAR))
        return round(realised, 6)


def build_instrument_states(instruments: dict) -> dict[str, InstrumentState]:
    """
    Initialises one InstrumentState per instrument from config.
    Call this once at simulator startup, not on every tick.
    """
    states = {}
    for symbol, meta in instruments.items():
        states[symbol] = InstrumentState(
            symbol        = symbol,
            current_price = meta["base_price"],
            volatility    = meta["volatility"],
        )
    return states
