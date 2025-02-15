"""
Import as:

import defi.dao_cross.order as ddacrord
"""

import logging
from typing import Optional, Union

import numpy as np
import pandas as pd

import helpers.hdbg as hdbg
import helpers.hdatetime as hdateti

_LOG = logging.getLogger(__name__)


class Order:
    """
    Create order for DaoCross or DaoSwap.
    """

    def __init__(
        self,
        base_token: str,
        quote_token: str,
        action: str,
        quantity: float,
        limit_price: Optional[float],
        timestamp: Optional[pd.Timestamp],
        deposit_address: Union[int, str],
        wallet_address: Union[int, str],
    ) -> None:
        """
        Constructor.

        :param base_token: token to express order quantity
        :param quote_token: token to express order price
        :param action: order action type
            - "buy": purchase the base token and pay with the quote token
            - "sell": sell the base token and receive the quote token
        :param quantity: quantity in terms of the base token
        :param limit_price: limit price in terms of the quote token per base token
        :param timestamp: time of order execution
            - if `None`, current timestamp is used
        :param deposit_address: deposit address to implement the order for
        :param wallet_address: wallet address to implement the order for
        """
        hdbg.dassert_isinstance(base_token, str)
        hdbg.dassert_isinstance(quote_token, str)
        hdbg.dassert_lte(0, quantity)
        hdbg.dassert_in(action, ["buy", "sell"])
        self.base_token = base_token
        self.quote_token = quote_token
        self.action = action
        self.quantity = quantity
        # Replace NaN with signed `np.inf` depending upon `action`.
        # This helps with `Order` comparisons (`lt` and `gt`).
        if np.isnan(limit_price):
            if self.action == "buy":
                self.limit_price = np.inf
            elif self.action == "sell":
                self.limit_price = -np.inf
            else:
                raise ValueError("Invalid action='%s'" % self.action)
        else:
            self.limit_price = limit_price
        # Use current time of execution if timestamp is not specified.
        if timestamp:
            hdbg.dassert_type_is(timestamp, pd.Timestamp)
            self.timestamp = timestamp
        else:
            self.timestamp = hdateti.get_current_time(tz="UTC")
        self.deposit_address = deposit_address
        self.wallet_address = wallet_address

    def __repr__(self) -> str:
        return str(self)

    def __str__(self) -> str:
        ret = (
            "base_token=%s quote_token=%s action=%s quantity=%s limit_price=%s timestamp=%s deposit_address=%s wallet_address=%s"
            % (
                self.base_token,
                self.quote_token,
                self.action,
                self.quantity,
                self.limit_price,
                self.timestamp,
                self.deposit_address,
                self.wallet_address,
            )
        )
        return ret

    def __lt__(self, other: "Order") -> bool:
        """
        Compare if order is lower in priority than the passed one.

        Because we use a min-heap, taking precedence in the order queue
        is given "lower priority" in the internal heap.
        """
        return self._takes_precedence(other)

    def __gt__(self, other: "Order") -> bool:
        """
        Compare if order is greater in priority than the passed one.
        """
        return not self._takes_precedence(other)

    def _takes_precedence(self, other: "Order") -> bool:
        """
        Compare order to another one according to quantity, price and
        timestamp. Prioritize orders according to:

            1. Quantity - higher quantity comes first in priority
            2. Price - higher limit price breaks quantity ties
            3. Timestamp - earlier timestamp breaks ties in quantity and price
        :param other: order to compare the actual order with
        :return: "True" if order preceeds the other one, "False" otherwise
        """
        takes_precedence = False
        if self.quantity > other.quantity:
            takes_precedence = True
        elif self.limit_price > other.limit_price:
            takes_precedence = True
        elif self.timestamp > other.timestamp:
            takes_precedence = True
        return takes_precedence


def get_random_order(seed: Optional[int] = None) -> Order:
    """
    Get an order for ETH/BTC with randomized valid parameters.
    """
    if seed is not None:
        np.random.seed(seed)
    base_token = "ETH"
    quote_token = "BTC"
    # Generate random buy/sells.
    action = "buy" if np.random.random() < 0.5 else "sell"
    # Generate random quantities.
    quantity = np.random.randint(1, 10)
    # Do not impose a limit price.
    limit_price = np.nan
    # Do not impose a timestamp.
    timestamp = np.nan
    # Create a random wallet address.
    deposit_address = np.random.randint(-3, 3)
    # Prevent self-crossing (in a crude way).
    if action == "buy":
        deposit_address = abs(deposit_address)
    elif action == "sell":
        deposit_address = -abs(deposit_address)
    # Make wallet address and deposit address the same.
    wallet_address = deposit_address
    # Build the order.
    order = Order(
        base_token,
        quote_token,
        action,
        quantity,
        limit_price,
        timestamp,
        deposit_address,
        wallet_address,
    )
    return order


def action_to_int(action: str) -> int:
    """
    Translate an action to an int.

    :param action: direction: `buy` or `sell`
    :return: int representation of a direction
    """
    ret = None
    if action == "buy":
        ret = 1
    elif action == "sell":
        ret = -1
    else:
        raise ValueError(f"Unsupported action={action}")
    return ret
