import ipaddress

def check_ip(ip: str) -> bool:
    try:
        ipaddress.ip_network(ip, strict=False)
        return True
    except ValueError:
        return False