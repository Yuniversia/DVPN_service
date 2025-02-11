import ipaddress

def check_ip(ip: str) -> bool:
    try:
        ipaddress.ip_network(ip, strict=False)
        return True
    except ValueError:
        return False
    
def gen_ip(ip: str, group_id: int) -> str:

    from app.models import search_ip
    ips = ipaddress.ip_network(ip, strict=False)
    ip_list = list(ips)

    ip_list.remove(ips.network_address)
    ip_list.remove(ips.broadcast_address)

    for ip_ in ip_list:
        if not search_ip(group_id, str(ip_)):
            return str(ip_)