import requests, json, re

url = "https://api.basescan.org/api/v2/api"
params = {
    "module": "transaction",
    "action": "gettxinfo",
    "txhash": "0x735d1f4da0da2f8f7b4ce4da543eba021576d815d3179754b577ef5e91019334"
}

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(url, params=params, headers=headers)

content_type = response.headers.get('content-type', '')
if 'application/json' in content_type:
    try:
        data = response.json()
        
        if 'result' in data and 'tokenTransferred' in data['result']:
            tt = data['result']['tokenTransferred']
            transfer = data['result'].get('transfer', {})
            
            print("Transaction details:")
            print(f"  Token name: {tt['token']['name']}")
            print(f"  Token symbol: {tt['token']['symbol']}")
            print(f"  Token value: {tt['value']}")
            print(f"  Decimals: {tt['token']['decimals']}")
            print()
            
            if transfer:
                print("Transfer details:")
                print(f"  From: {transfer.get('from')}")
                print(f"  To: {transfer.get('to')}")
                print(f"  Value (wei): {transfer.get('value')}")
                print(f"  Amount: {transfer.get('amount')}")
        else:
            print("No tokenTransferred field")
    else:
        print(f"Not JSON response. Content-Type: {content_type}")
