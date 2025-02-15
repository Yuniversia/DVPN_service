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
        
def is_valid_name(name: str) -> bool:
    """
    Проверяет, является ли имя валидным.
    - Не должно содержать специальных символов (кроме пробела, дефиса и апострофа).
    - Не может быть пустым или состоять только из пробелов.
    - Допускаются буквы любых языков.
    """
    # Удаляем начальные и конечные пробелы
    stripped_name = name.strip()
    
    # Проверка на пустую строку
    if not stripped_name:
        return False
    
    # Проверка каждого символа
    allowed_chars = {' ', '-', "'"}
    for char in stripped_name:
        if not (char.isalpha() or char in allowed_chars):
            return False
    
    return True