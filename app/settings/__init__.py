# -*- coding: utf-8 -*-

from __future__ import absolute_import
import logging
import os
import sys
import json

import fakeredis
from honeybadger import honeybadger
import redis.exceptions
from walrus import Database


def honeybadger_handler(req, resp, exc, params):
    """Custom error handler for exception notifications."""
    if exc is None:
        return

    req_data = dict(
        remote_address=req.access_route,
        url=req.uri,
        method=req.method,
        content_type=req.content_type,
        headers=req.headers,
        params=req.params,
        query_string=req.query_string
    )

    honeybadger.notify(exc, context=dict(request=req_data))

    # Use default response handler...
    from ..app import app
    app._python_error_handler(req, resp, exc, params)


# Logger setup...
LOGGER = logging.getLogger(__name__)
LOGGER.addHandler(logging.StreamHandler(sys.stdout))
LOGGER.setLevel(os.getenv('LOGGING_LEVEL', 'DEBUG'))

# Tokenlists are split with a pipe char (unlikely to be used in URIs)
TOKENLISTS = os.getenv('TOKENLISTS', '').split('|')
DEFAULT_TOKEN_ADDRESS = os.getenv('DEFAULT_TOKEN_ADDRESS').lower()
STABLE_TOKEN_ADDRESS = os.getenv('STABLE_TOKEN_ADDRESS').lower()
ROUTE_TOKEN_ADDRESSES = \
    os.getenv('ROUTE_TOKEN_ADDRESSES', '').lower().split(',')
IGNORED_TOKEN_ADDRESSES = \
    os.getenv('IGNORED_TOKEN_ADDRESSES', '').lower().split(',')
# Will be picked automatically by web3.py
WEB3_PROVIDER_URI = os.getenv('WEB3_PROVIDER_URI')
PRIVATE_KEY = os.getenv('PRIVATE_KEY')

FACTORY_ADDRESS = os.getenv('FACTORY_ADDRESS')
VOTER_ADDRESS = os.getenv('VOTER_ADDRESS')
ROUTER_ADDRESS = os.getenv('ROUTER_ADDRESS')
VE_ADDRESS = os.getenv('VE_ADDRESS')
REWARDS_DIST_ADDRESS = os.getenv('REWARDS_DIST_ADDRESS')
WRAPPED_BRIBE_FACTORY_ADDRESS = os.getenv('WRAPPED_BRIBE_FACTORY_ADDRESS')
X_WRAPPED_BRIBE_FACTORY_ADDRESS = os.getenv('X_WRAPPED_BRIBE_FACTORY_ADDRESS')
XX_WRAPPED_BRIBE_FACTORY_ADDRESS = os.getenv('XX_WRAPPED_BRIBE_FACTORY_ADDRESS')
X_WRAPPED_BRIBE_ABI = json.loads('[{"inputs":[{"internalType":"address","name":"_voter","type":"address"},{"internalType":"uint256","name":"_csrNftId","type":"uint256"}],"stateMutability":"nonpayable","type":"constructor"},{"inputs":[],"name":"TURNSTILE","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"existing_bribe","type":"address"}],"name":"createBribe","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"nonpayable","type":"function"},{"inputs":[],"name":"csrNftId","outputs":[{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"last_bribe","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"address","name":"","type":"address"}],"name":"oldBribeToNew","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"voter","outputs":[{"internalType":"address","name":"","type":"address"}],"stateMutability":"view","type":"function"}]')

# Seconds to wait before running the chain syncup. `0` disables it!
SYNC_WAIT_SECONDS = int(os.getenv('SYNC_WAIT_SECONDS', 0))

# Placeholder for our cache instance (Redis).
CACHE = None

try:
    CACHE = Database.from_url(os.getenv('REDIS_URL', ''))
    CACHE.ping()
except (ValueError, redis.exceptions.ConnectionError):
    LOGGER.debug('No Redis server found, using memory ...')
    # Patch walrus duh...
    # See: https://github.com/coleifer/walrus/issues/95
    db_class = Database
    db_class.__bases__ = (fakeredis.FakeRedis,)
    CACHE = db_class()
