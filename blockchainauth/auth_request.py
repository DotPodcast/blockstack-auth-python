#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    ~~~~~
    :copyright: (c) 2015 by Halfmoon Labs, Inc.
    :license: MIT, see LICENSE for more details.
"""
import uuid
import time
from cryptography.hazmat.backends import default_backend
from pybitcoin import BitcoinPrivateKey
from .auth_message import AuthMessage
from .dids import make_did_from_address
from .tokenizer import Tokenizer
from .verification import is_expiration_date_valid, is_issuance_date_valid, \
    do_signatures_match_public_keys, do_public_keys_match_issuer


class AuthRequest(AuthMessage):
    """ Interface for creating signed auth request tokens, as well as decoding
        and verifying them.
    """

    verify_methods = [
        is_expiration_date_valid,
        is_issuance_date_valid,
        do_signatures_match_public_keys,
        do_public_keys_match_issuer
    ]

    def __init__(self, private_key, domain_name, manifest_uri=None, redirect_uri=None,
                 scopes=None, expires_at=None, crypto_backend=default_backend()):
        """ private_key should be provided in HEX, WIF or binary format 
            domain_name should be a valid domain
            manifest_uri should be a valid URI
            redirect_uri should be a valid URI
            scopes should be a list
            expires_at should be a float number of seconds since the epoch
        """
        if not manifest_uri:
            manifest_uri = domain_name + '/manifest.json'

        if not redirect_uri:
            redirect_uri = domain_name

        if not scopes:
            scopes = []

        if not expires_at:
            expires_at = time.time() + 3600  # next hour

        self.private_key = private_key
        self.domain_name = domain_name
        self.manifest_uri = manifest_uri
        self.redirect_uri = redirect_uri
        self.scopes = scopes
        self.expires_at = expires_at
        self.tokenizer = Tokenizer(crypto_backend=crypto_backend)

    def _payload(self):
        payload = {
            'jti': str(uuid.uuid4()),
            'iat': str(time.time()),
            'exp': str(self.expires_at),
            'iss': None,
            'public_keys': [],
            'domain_name': self.domain_name,
            'manifest_uri': self.manifest_uri,
            'redirect_uri': self.redirect_uri,
            'scopes': self.scopes
        }
        if self.private_key:
            public_key = BitcoinPrivateKey(self.private_key).public_key()
            address = public_key.address()
            payload['public_keys'] = [public_key.to_hex()]
            payload['iss'] = make_did_from_address(address)
        return payload
