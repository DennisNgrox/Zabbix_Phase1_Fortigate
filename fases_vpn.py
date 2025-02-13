import json
import re
import os
from zabbix_utils import ZabbixAPI

zapi = ZabbixAPI(
    url="", 
    token=""
    # ,validate_certs=False
)

triggers = zapi.trigger.get({
    "output": ["description", "value"],
    "selectItems": ["key_"],
    "hostids": 10698,
    "expandDescription": 1,
    "filter": {
        "status": 0
    }
})

# Filtra as triggers cuja descrição corresponde ao padrão "VPN VPN-.*"
vpn_triggers = [
    {
        "triggerid": trigger['triggerid'],
        "description": trigger['description'],
        "value": trigger['value'],
        "fase1_index": re.sub(r"vpn.tunnel.status\[fgVpnTunEntStatus.(\d+).\d+\]", r"\1", trigger['items'][0]['key_'])
    } for trigger in triggers
    if re.search(r"VPN VPN-.*", trigger["description"])
]

index_full_list = [ i["fase1_index"] for i in vpn_triggers ]
index_list = list(set(index_full_list))

data = []
for i in index_list:
    d1 = [ vpn for vpn in vpn_triggers if vpn["fase1_index"] == i ]
    prefix_list = [ re.sub(r"VPN (.*):.*", r"\1", j["description"]) for j in d1 ]
    prefix = os.path.commonprefix(prefix_list)
    len1 = len(d1)
    sum1 = sum(int(k["value"]) for k in d1)
    msg = "VPN is Down" if len1 == sum1 else "VPN is Up"
    data.append({
        "index": i,
        "prefix": prefix,
        "total": len1,
        "down": sum1,
        "msg": msg
    })

print(json.dumps(data, indent=4))


