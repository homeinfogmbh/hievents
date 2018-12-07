"""Configuration parser."""

from configlib import INIParser

__all__ = ['CONFIG']


CONFIG = INIParser('/usr/local/etc/hievents.conf')
