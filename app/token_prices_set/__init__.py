# -*- coding: utf-8 -*-

token_prices = set()

class TokenPrices():
    """This is a workaround class for updating prices each sync iteration."""

    @classmethod
    def is_in_token_prices_set(cls, address):
        """Checks if token address is in global set"""
        global token_prices
        result = False
        if address.lower() in token_prices:
            result = True
        return result

    @classmethod
    def update_token_prices_set(cls, address):
        """Adds token address to global set"""
        global token_prices
        token_prices.add(address.lower())
