# vpn_project/socketio_app.py

import socketio
import logging
from vpn_app.models import CustomUser, Group

logger = logging.getLogger(__name__)

# Используем Eventlet для асинхронности, как наиболее совместимый с Django
sio = socketio.Server(async_mode='eventlet', cors_allowed_origins='*')

# {sid: {'user_id': user.id, 'username': user.username, 'peer_id': peer_id, 'group_id': group_id}}
connected_users_data = {}

@sio.event
def connect(sid, environ):
    logger.info(f"Socket.IO client connected: {sid}")
    # Мы не знаем пользователя, пока он не аутентифицируется
    connected_users_data[sid] = {}


@sio.event
def disconnect(sid):
    logger.info(f"Socket.IO client disconnected: {sid}")
    
    if sid in connected_users_data:
        user_data = connected_users_data.get(sid, {})
        peer_id = user_data.get('peer_id')
        group_id = user_data.get('group_id')

        # Если пользователь был в группе, оповещаем остальных
        if peer_id and group_id:
            try:
                sio.emit('peer_removed', {'peer_id': peer_id}, room=str(group_id))
                logger.info(f"Emitted peer_removed for {peer_id} in group {group_id} on disconnect")
            except Exception as e:
                logger.error(f"Error emitting peer_removed: {e}")
        
        # Удаляем пользователя из нашего отслеживания
        del connected_users_data[sid]


@sio.event
def authenticate_peer(sid, data):
    """
    Клиент должен отправить это событие после подключения,
    передав свой 'peer_id' и токен (здесь не реализовано, но подразумевается).
    Для простоты, будем доверять 'peer_id' и 'user_id' (или 'session_key').
    В вашем views.py вы полагаетесь на user.id, что сложно получить в socketio
    напрямую без сессии.
    
    Упрощенная версия: клиент присылает peer_id.
    Мы должны найти пользователя по этому peer_id.
    """
    
    peer_id = data.get('peer_id')
    if not peer_id:
        logger.warning(f"Client {sid} tried to authenticate without peer_id")
        return {"status": "error", "message": "peer_id is required"}

    try:
        user = CustomUser.objects.get(peer_id=peer_id)
    except CustomUser.DoesNotExist:
        logger.warning(f"Authentication failed: No user found for peer_id {peer_id} (SID: {sid})")
        return {"status": "error", "message": "User not found for this peer_id"}

    if not user.current_group:
        logger.warning(f"User {user.username} (peer_id: {peer_id}) is not in a group.")
        return {"status": "error", "message": "User is not currently in a group"}

    group = user.current_group
    group_id = str(group.id)

    # Обновляем данные о подключенном пользователе
    connected_users_data[sid] = {
        'user_id': user.id,
        'username': user.username,
        'peer_id': peer_id,
        'group_id': group_id
    }

    # Добавляем пользователя в комнату его группы
    sio.enter_room(sid, group_id)
    logger.info(f"User {user.username} (SID: {sid}, Peer: {peer_id}) authenticated and joined group room {group_id}")

    # 1. Получаем список всех пиров в группе
    initial_peer_list = []
    # Сначала найдем всех, кто онлайн (в нашей connected_users_data)
    online_peers_in_group = {
        data['user_id']: data for s_id, data in connected_users_data.items()
        if data.get('group_id') == group_id and s_id != sid # Все, кроме текущего
    }

    # Затем пройдемся по всем членам группы из БД
    group_members = CustomUser.objects.filter(current_group=group)
    
    current_user_peer_data = None

    for member in group_members:
        is_self = (member.id == user.id)
        
        online_data = online_peers_in_group.get(member.id)
        
        peer_data = {
            'name': member.username,
            'addr': member.group_ip,
            'peer_id': online_data.get('peer_id') if online_data else (member.peer_id if is_self else None),
            'online': True if online_data or is_self else False
        }
        
        if is_self:
            current_user_peer_data = peer_data # Сохраняем данные текущего пользователя
        else:
            initial_peer_list.append(peer_data)


    # 2. Отправляем текущему пользователю список всех *других* пиров
    sio.emit('initial_peer_list', {'peers': initial_peer_list}, room=sid)
    logger.info(f"Sent initial_peer_list of {len(initial_peer_list)} peers to {user.username} (SID: {sid})")

    # 3. Оповещаем *всех остальных* в группе о *новом* пире
    if current_user_peer_data:
        # Убедимся, что отправляем правильный peer_id
        current_user_peer_data['peer_id'] = peer_id
        current_user_peer_data['online'] = True
        
        sio.emit('peer_added', {'peer': current_user_peer_data}, room=group_id, skip_sid=sid)
        logger.info(f"Emitted peer_added for {user.username} (Peer: {peer_id}) to group {group_id}")

    return {"status": "success", "message": "Authenticated successfully"}