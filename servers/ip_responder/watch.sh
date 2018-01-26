#!/usr/bin/env bash

journalctl --lines 0 --follow _SYSTEMD_UNIT=ip_responder.service

