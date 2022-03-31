#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This runs the supplementary admin agent for Windows

from __future__ import absolute_import
from fortrace.core.winadminagent import WinAdminAgent

def main():
    a = WinAdminAgent()
    a.process()

if __name__ == "__main__":
    try:
        main()
    except:
        sys.exit(1)
