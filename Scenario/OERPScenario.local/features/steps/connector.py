# -*- coding: utf-8 -*-
from support import *
import datetime
import csv
import os.path as osp
import pprint

@given('I press the button "{button}"')
def impl(ctx, button):
    backend = ctx.found_item
    assert backend
    getattr(backend, button)()
