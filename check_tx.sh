#!/bin/bash
curl -s "https://api.basescan.org/api/v2/api?module=transaction&action=gettxinfo&txhash=0x735d1f4da0da2f8f7b4ce4da543eba021576d815d3179754b577ef5e91019334" | python3 -m json.tool 2>&1 | grep -E "(Value|Amount)"
