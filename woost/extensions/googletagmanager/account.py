#-*- coding: utf-8 -*-
u"""

.. moduleauthor:: Eduard Nadal <eduard.nadal@whads.com>
"""
import re
from cocktail.schema import String


class GoogleTagManagerAccount(String):

    account_id_reg_expr = re.compile(
        r"www\.googletagmanager\.com/ns\.html\?id=(?P<account>[a-zA-Z0-9\-_]+)"
    )

    def normalization(self, value):
        if value:
            match = self.account_id_reg_expr.search(value)
            if match:
                value = match.group("account")
        return value

