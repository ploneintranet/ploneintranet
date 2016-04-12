# coding=utf-8
from DateTime import DateTime
import os

UPLOADS = os.path.join(os.path.dirname(__file__), 'uploads')
YESTERDAY = (DateTime() - 1).strftime('%Y-%m-%d')
