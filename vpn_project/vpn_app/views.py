from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, FileResponse, Http404
from django.utils import timezone
from django.urls import reverse
from django.db.utils import IntegrityError
from vpn_project.socketio_app import sio, connected_users_data
from django.conf import settings
# from .forms import LoginForm, RegisterForm # Вам нужно будет создать эти формы
from .models import CustomUser, Group, Link, Peer_link

import datetime # для InviteLink
import logging
import ipaddress
import uuid
import os
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

load_dotenv()

def index_view(request):

    context = {
        "win_module_path": os.getenv('WIN_MODULE_PATH'),
        "linux_module_path": os.getenv('LINUX_MODULE_PATH'),
        "dvpn_arm_path": os.getenv('DVPN_ARM_LATEST_PATH'),
        "dvpn_amd_path": os.getenv('DVPN_AMD_LATEST_PATH'),
        "dvpn_ubuntu_path": os.getenv('DVPN_UBUNTU_LATEST_PATH'),
        "dvpn_win_path": os.getenv('DVPN_WINDOWS_LATEST_PATH')
    }

    return render(request, 'vpn_app/index.html', context)

def login_register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    return render(request, 'vpn_app/login.html') # Упрощенно для примера HTML

def login_user(request):
    if request.method == 'POST':
        # Логика входа пользователя
        username_or_email = request.POST.get('username_or_email')
        password = request.POST.get('password')

        user = authenticate(request, username=username_or_email, password=password)

        if user is None:
            user = authenticate(request, email=username_or_email, password=password)
            print(user)

        if user is not None:
            login(request, user)
            next_url = request.GET.get('next')
            
            # Вместо redirect, возвращаем JSON, который сообщает клиенту, куда перейти
            answer = {
                "message": "Вход выполнен успешно. Перенаправление...",
                "element": "login",
                "process": "success",
                "reload": False, # Не перезагружаем автоматически, даем URL
                "redirect_url": next_url if next_url else '/dashboard/' # Указываем URL для перенаправления
            }
            return JsonResponse(answer)

        else:
            answer = {
                "message": "Не верный логин или пароль",
                "element": "login",
                "process": "error",
                "reload": False
            }
            return JsonResponse(answer)

    return redirect('login_register_page')

def register_user(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if not username.isalnum(): # Проверка на пренадлежность к a-z, A-Z, 0-9. Если нет, вызывает ошибку
            answer = {
                "message": "Имя не может быть пустым или состоять из специальных символов. Только буквы и цифры.",
                "element": "name",
                "process": "error",
                "reload": False 
            }
            return JsonResponse(answer)

        if len(password) < 7:
            answer = {
                "message": "Пароль должен быть больше 8 символов",
                "element": "login-password",
                "process": "error",
                "reload": False 
            }
            return JsonResponse(answer)

        try: # Проверка уникальности имени / почты
            user = CustomUser.objects.create_user(username, email, password)
        except IntegrityError:
            answer = {
                "message": "Данная почта или имя уже зарегистрированы",
                "element": "name",
                "process": "error",
                "reload": False 
            }
            return JsonResponse(answer)
        
        user.backend = 'django.contrib.auth.backends.ModelBackend'
        login(request, user)
        next_url = request.GET.get('next')

        answer = {
                "message": "Вход выполнен успешно. Перенаправление...",
                "element": "name",
                "process": "success",
                "reload": False, # Не перезагружаем автоматически, даем URL
                "redirect_url": next_url if next_url else '/dashboard/' # Указываем URL для перенаправления
            }
        return JsonResponse(answer, status=200)

    return redirect('login_register_page')

@login_required
def logout_user(request):
    logout(request)
    return redirect('index')

@login_required
def dashboard_view(request):
    user = request.user
    user_has_group = True if user.current_group is not None else False 

    if not user_has_group:
        context = {
        'user_has_group': user_has_group,
        'user': request.user 
        }

    else:
        group = user.current_group
        group_members = CustomUser.objects.all().filter(current_group=group.id)

        context = {
        'user_has_group': user_has_group,
        'group': group,
        'group_members': group_members,
        'user': request.user
        }

    return render(request, 'vpn_app/dashboard.html', context)


@login_required
def create_group(request):
    if request.method == 'POST':
        group_name = request.POST.get('group_name')
        group_ip = request.POST.get('group_ip')

        try:
            group = Group.objects.get(name=group_name)
            answer = {
                "message": "Такое имя группы уже существует",
                "element": "group",
                "process": "error",
                "reload": False
            }
            return JsonResponse(answer)
        except Group.DoesNotExist:

            user_id = request.user.id
            
            if user_id:
                db_user = CustomUser.objects.get(id=user_id)

                try:
                    ipaddress.ip_network(group_ip, strict=False)
                except ValueError:
                    answer = {
                    "message": "Неккоректный айпи",
                    "element": "ip",
                    "process": "error",
                    "reload": False
                    }
                    return JsonResponse(answer)
                
                # Создаем новую группу
                new_group = Group.objects.create(name=group_name, ip_address=group_ip, creator = db_user)
                new_group.save()
                
                # Добавляем пользователя как админа
                new_group.group_admins.add(db_user)
                
                # Обновляем текущую группу пользователя
                db_user.group_ip = gen_ip(new_group.id)
                db_user.current_group = new_group
                db_user.save()

                answer = {
                    "message": "Неккоректный айпи",
                    "element": "None",
                    "process": "success",
                    "reload": True
                    }
                return JsonResponse(answer)
                
                return redirect('dashboard') # Не обновляет страницу
            else:
                # Обработка случая, когда ID пользователя отсутствует
                print("User ID is None, authentication issue")
                return redirect('login')  # Перенаправление на страницу входа
    
    return redirect('dashboard')  # или на страницу с формой, если GET


@login_required
def join_group_view(request, id):

    if request.method == "POST":

        id = request.POST.get('link_id')
        user = request.user
        link_obj = Link.objects.get(link_code = id)

        if link_obj and is_link_active(link_obj):
                group = link_obj.group
                # Проверяем, если пользователь уже состоит в какой-либо группе
                if user.current_group:

                    # Отключаем пользователя от старой комнаты Socket.IO, если он был онлайн
                    for sid, data in list(connected_users_data.items()): # Создаем копию, так как итерируемся и изменяем
                        if data.get('user_id') == user.id:
                            old_group_id = str(user.current_group.id)
                            sio.leave_room(sid, old_group_id)
                            peer_id = data.get('peer_id')
                            if peer_id:
                                # Отправляем peer_removed в старую группу, если пользователь был онлайн
                                sio.emit('peer_removed', {'peer_id': peer_id}, room=old_group_id)
                                print(f"Peer {peer_id} (user {user.username}) удален из старой группы {old_group_id} при переключении.")
                            break # Нашли и обработали SID пользователя

                # Генерация IP для пользователя в новой группе
                available_ip = gen_ip(group.id)
                if available_ip:
                    user.current_group = group
                    user.group_ip = str(available_ip)
                    user.save()

                    # После обновления данных пользователя, если он онлайн по Socket.IO,
                    # нужно заставить его переподключиться или заново аутентифицировать peer_id,
                    # чтобы он получил новый initial_peer_list и был анонсирован.
                    # Самый простой способ - предложить клиенту переподключиться к Socket.IO.
                    # Или, если он уже подключен, вызвать authenticate_peer снова.
                    for sid, data in list(connected_users_data.items()):
                        if data.get('user_id') == user.id:
                            # Это должен сделать клиент после того, как узнает, что он в новой группе
                            # Или, если хотим, чтобы сервер это сделал:
                            sio.emit('reauthenticate_required', room=sid) # Сообщаем клиенту
                            # Тогда клиент в module.py должен поймать это событие

                            pass # Ничего не делаем здесь, так как authenticate_peer в socketio_app.py
                                # сам обрабатывает вход в комнату и анонс.
                                # Если пользователь уже был в группе и просто меняет IP,
                                # authenticate_peer при переподключении сам отправит правильные данные.

                    answer = {
                    "message": f"Вы успешно присоединились к группе {group.name} с IP {available_ip}.",
                    "element": "None",
                    "process": "success",
                    "reload": False,
                    "redirect_url": "/dashboard"
                    }

                    return JsonResponse(answer)
                else:
                    return JsonResponse({"status": "error", "message": "Нет доступных IP-адресов в этой группе."}, status=400)
        else:
            return JsonResponse({"status": "error", "message": "Неверный или неактивный код приглашения."}, status=400)
        
    if request.method == 'GET':
        link_id = id

        link_obj = Link.objects.get(link_code = link_id)

        if link_obj and is_link_active(link_obj):

            group = Group.objects.get(id = link_obj.group_id)

            redirect_url = reverse('group_invite_modal') + f'?group_id={group.id}&link={link_id}'

            return redirect(redirect_url)
        
        return JsonResponse({"status": "error", "message": "Ccылка не активна."}, status=405)

    return JsonResponse({"status": "error", "message": "Недопустимый метод запроса."}, status=405)

@login_required
def group_invite_modal(request):

    if request.method == 'GET':

        group = Group.objects.get(id = request.GET.get('group_id'))
        link_id = request.GET.get('link')

        member_count = len(CustomUser.objects.filter(current_group_id = group.id))
        creator = CustomUser.objects.get(id = group.creator_id)

        context = {
            'group': group,
            'link_id': link_id,
            'user': request.user,
            'creator': creator,
            'member_count': member_count
            }

        return render(request, 'vpn_app/join_group.html', context)
    
    return Http404

@login_required
def join_group_menu(request):
    if request.method == 'POST':
        link = request.POST.get('invite_code')

        if link[0:4] == "http":
            id = link[-36:]
        else:
            id = link

        try:
            link_obj = Link.objects.get(link_code = id)
        except:
            answer = {
                "message": "Ссылка не найдена",
                "element": "link_menu",
                "process": "error",
                "reload": False}
            return JsonResponse(answer)
        
        ans = link_validation(link_obj)
        if ans:
            return JsonResponse(ans)
        
        request.user.current_group = link_obj.group

        ip = gen_ip(link_obj.group.id)
        if ip is False:
            answer = {
                "message": "Нет свободных айпи в группе",
                "element": "None",
                "process": "error",
                "reload": False}
            return JsonResponse(answer)
        
        request.user.group_ip = ip
        request.user.save()

        if link_obj.is_admin_link:
            link_obj.group.group_admins.add(request.user)

        link_obj.current_uses += 1
        link_obj.save()

        group_id = str(link_obj.group.id)
        new_peer_data = {
            'name': request.user.username,
            'addr': request.user.group_ip,
            'peer_id': request.user.peer_id
        }
        sio.emit('peer_added', {'peer': new_peer_data}, room=group_id)

        answer = {
                "message": "Успешно добавлен в группу",
                "element": "None",
                "process": "success",
                "reload": True}
        return JsonResponse(answer)

        answer = {
                "message": "Успешно добавлен в группу",
                "element": "None",
                "process": "success",
                "reload": True}
        return JsonResponse(answer)
            
            
    
    
def link_validation(link):
    if not link:
        answer = {
            "message": "Такая ссылка небыла найдена",
            "element": "None",
            "process": "error",
            "reload": False}
        return answer
    
    
    if not is_link_active(link):
        answer = {
            "message": "Ссылка изтекла по времени или использованиям",
            "element": "None",
            "process": "error",
            "reload": False}
        return answer


def gen_ip(group_id: int) -> str | None:
    """
    Находит первый свободный IP-адрес для заданной группы в пределах ее IP-диапазона,
    начиная поиск с указанного в group.ip_address.

    Args:
        group_id: ID группы, для которой нужно найти IP.

    Returns:
        Первый свободный IP-адрес в виде строки,
        или None, если свободный IP не найден, группа не существует,
        или IP-адрес группы недействителен.
    """
    try:
        # 1. Получаем объект группы по ее ID.
        group = Group.objects.get(id=group_id)

        # 2. Проверяем, задан ли IP-адрес для группы.
        if not group.ip_address:
            print(f"Ошибка: Для группы с ID {group_id} не указан IP-адрес.")
            return None

        # Разделяем IP-адрес и префикс маски
        ip_str, prefix_len_str = group.ip_address.split('/')
        prefix_len = int(prefix_len_str)

        # 3. Преобразуем строковое представление IP-сети (CIDR) в объект ipaddress.
        network = ipaddress.ip_network(group.ip_address, strict=False)

        # Определяем начальный IP для итерации.
        # Это будет IP-адрес, указанный в group.ip_address, если он валиден.
        start_ip = ipaddress.ip_address(ip_str)

        # Проверяем, находится ли start_ip в пределах определенной сети.
        if start_ip not in network:
            print(f"Ошибка: Указанный начальный IP {start_ip} не принадлежит сети {network}.")
            return None

        # 4. Получаем все IP-адреса, уже используемые пользователями в данной группе.
        used_ips_in_group = CustomUser.objects.filter(
            current_group=group
        ).values_list('group_ip', flat=True)
        used_ips_set = set(used_ips_in_group)

        # 5. Итерируем по всем доступным хостовым IP-адресам в сети,
        #    начиная с `start_ip`.
        #    Важно: network.hosts() по-прежнему будет генерировать их с начала сети,
        #    поэтому нам нужно отфильтровать или найти точку старта.

        found_start = False
        for ip_address in network.hosts():
            if not found_start:
                if ip_address == start_ip:
                    found_start = True
                else:
                    # Пропускаем IP-адреса до start_ip
                    continue

            if str(ip_address) not in used_ips_set:
                return str(ip_address)

        print(f"Для группы с ID {group_id} нет свободных IP-адресов в диапазоне, начиная с {start_ip}.")
        return None

    except ValueError as e:
        print(f"Ошибка парсинга IP-адреса или префикса: {e}")
        return None
    except ipaddress.AddressValueError:
        print(f"Ошибка: Неверный формат IP-адреса для группы ID {group_id}: {group.ip_address}")
        return None
    except Group.DoesNotExist:
        print(f"Ошибка: Группа с ID {group_id} не найдена.")
        return None
    except Exception as e:
        print(f"Произошла непредвиденная ошибка: {e}")
        return None
    

@login_required
def generate_invite_link(request):
    uses = request.POST.get('uses')
    expiry = request.POST.get('expiry')
    is_admin = request.POST.get('make_admin')

    group = request.user.current_group

    if expiry == 0:
        expiry = None
    
    if is_admin is None:
        is_admin = False
    else:
        is_admin = True
    
    link = Link.objects.create(author=request.user, group=group, expires_in_hours=int(expiry),
                                is_admin_link = is_admin, link_code = str(uuid.uuid4()), max_uses = uses)
    
    link.save()

    answer = {
            "link": f"https://dvpn.yuniversia.eu/group/join/{link.link_code}"
    }
    return JsonResponse(answer)

@login_required
def remove_member(request, member_id):
        
    if request.method == 'DELETE':
        try:
            member_to_remove = CustomUser.objects.get(id=member_id)
            current_user_group = request.user.current_group

            if member_to_remove.current_group == current_user_group and request.user == current_user_group.creator:

                # Отправляем событие peer_removed всем членам группы
                group_id = str(current_user_group.id)

                # Находим peer_id удаляемого пользователя, если он онлайн
                removed_peer_id = None
                for sid, data in list(connected_users_data.items()):
                    if data.get('user_id') == member_to_remove.id:
                        removed_peer_id = data.get('peer_id')
                        if removed_peer_id:
                            sio.emit('peer_removed', {'peer_id': removed_peer_id}, room=group_id)
                            print(f"Peer {removed_peer_id} (user {member_to_remove.username}) удален из группы {group_id} по запросу админа.")
                        # Также отключаем SID этого пользователя от комнаты группы
                        sio.leave_room(sid, group_id)
                        break

                member_to_remove.current_group = None
                member_to_remove.group_ip = None
                member_to_remove.save()
                return HttpResponse('200')
            return HttpResponse('403') # Недостаточно прав
        except CustomUser.DoesNotExist:
            return HttpResponse('404') # Пользователь не найден
    return HttpResponse('405') # Недопустимый метод

@login_required
def leave_group(request, id): 
    user = request.user
    if request.method == 'GET':
        if user.current_group:
            group = user.current_group
            group_id = str(group.id)



            # Отправляем событие peer_removed
            # Находим peer_id текущего пользователя, если он онлайн
            current_peer_id = None
            for sid, data in list(connected_users_data.items()):
                if data.get('user_id') == user.id:
                    current_peer_id = data.get('peer_id')
                    if current_peer_id:
                        sio.emit('peer_removed', {'peer_id': current_peer_id}, room=group_id)
                        print(f"Peer {current_peer_id} (user {user.username}) покинул группу {group_id}.")
                    # Также отключаем SID этого пользователя от комнаты группы
                    sio.leave_room(sid, group_id)
                    break

            user.current_group = None
            user.group_ip = None
            user.save()
            return HttpResponse('200')
        return HttpResponse('400') # Пользователь не состоит в группе
    return HttpResponse('405') # Недопустимый метод

@login_required
def delete_group(request, id):
    group_id = id
    try:
            group = Group.objects.get(id=group_id)
            if request.user == group.creator:
                # Сначала удаляем всех пользователей из группы и их IP
                members_to_clear = CustomUser.objects.filter(current_group=group)
                for member in members_to_clear:

                    member.current_group = None
                    member.group_ip = None
                    member.save()
                    # Если пользователь был онлайн, сообщаем всем об его удалении
                    for sid, data in list(connected_users_data.items()):
                        if data.get('user_id') == member.id:
                            member_peer_id = data.get('peer_id')
                            if member_peer_id:
                                sio.emit('peer_removed', {'peer_id': member_peer_id}, room=str(group_id))
                            sio.leave_room(sid, str(group_id)) # Удаляем из комнаты
                            break

                # Отправляем событие в комнату ПЕРЕД тем, как все ее покинут
                sio.emit('group_deleted', {'message': 'Группа была удалена ее создателем'}, room=str(group_id))
                sio.close_room(room=str(group_id)) # Закрываем комнату на сервере

                group.delete()
                return HttpResponse('200')
            return HttpResponse('403')
    except Group.DoesNotExist:
        return HttpResponse('404')
    return HttpResponse('405')

@login_required
def share_peerlist(request):

    user = request.user
    group = Group.objects.get(id = user.current_group_id)
    link = os.urandom(6).hex()

    new_peer_link = Peer_link.objects.create(link = link, creator = user, group = group)
    new_peer_link.save()
    
    answer = {
            "link": f"https://dvpn.yuniversia.eu/group/peers/{link}"
    }
    return JsonResponse(answer)

def get_peers(request, link):
    obj = Peer_link.objects.get(link = link)
    group_id = obj.group.id

    peers = []
    members = CustomUser.objects.filter(current_group_id = group_id)

    for peer in members:
        # Для DVPN-клиента важен peer_id, который он получает по Socket.IO.
        peer_data_from_socketio = None
        for sid, data in connected_users_data.items():
            if data.get('user_id') == peer.id:
                peer_data_from_socketio = data
                break

        peers.append({
            'name': peer.username,
            'django_id': peer.id,
            'addr': peer.group_ip,
            'peer_id': peer_data_from_socketio.get('peer_id') if peer_data_from_socketio else None, # Здесь будет актуальный peer_id, если пользователь онлайн
            'self': True if peer.id == obj.creator.id else False
        })

    return JsonResponse({'peers': peers})


# def download_file_streamed(request, filename):
#     """
#     Представление для загрузки файла из каталога static/files,
#     использующее потоковую передачу для эффективности.
#     """
#     file_path = os.path.join(settings.BASE_DIR, 'vpn_app', 'static', 'vpn_app', 'files', filename)

#     if os.path.exists(file_path):
#         # Открываем файл в бинарном режиме ('rb')
#         # FileResponse автоматически закроет файл после отправки
#         response = FileResponse(open(file_path, 'rb'))
        
#         # Устанавливаем заголовок Content-Type (опционально, но хорошо для точности)
#         # Если вы знаете конкретный тип, можете использовать его, например, 'image/png'
#         # Если нет, 'application/octet-stream' универсален
#         response['Content-Type'] = 'application/octet-stream' # FileResponse часто устанавливает его сам

#         # Устанавливаем заголовок Content-Disposition для скачивания файла
#         response['Content-Disposition'] = f'attachment; filename="{os.path.basename(file_path)}"'
        
#         return response
#     else:
#         raise Http404("Файл не найден.")


def error_page(request):
    if request.method == 'GET':

        status = request.GET.get('status')
        message = request.GET.get('message')

        context = {
            'status': status,
            'message': message
            }

        return render(request, 'vpn_app/error.html', context)
    
    return Http404
     
    

def is_link_active(link_obj):
    if link_obj.expiration_time and timezone.now() > link_obj.expiration_time:
        return False # Срок действия истек
    if link_obj.current_uses >= link_obj.max_uses:
        return False # Достигнуто максимальное количество использований
    return True