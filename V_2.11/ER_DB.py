import airtable
import strs
from config_file_prod import *
import pickle


airt_reg = airtable.Airtable(airt_app, airt_reg_tbl, airt_api_key)
airt_event = airtable.Airtable(airt_app, airt_event_tbl, airt_api_key)
airt_feedback = airtable.Airtable(airt_app, airt_feedback_tbl, airt_api_key)
airt_ppl = airtable.Airtable(airt_app, airt_ppl_tbl, airt_api_key)
airt_adlist = airtable.Airtable(airt_app, airt_adlist_tbl, airt_api_key)


def open_for_reg_events():  # вернёт словарь для регистрации {эвент с местам: [евент айди, булиан вэтлист или нет, булиан только ли для подписки]}
    future_events_resp = airt_event.get_all(view=airt_event_tbl_open_for_reg_view)
    future_events={}
    for i in range(len(future_events_resp)):
        ev_name_w_places=future_events_resp[i]['fields']['Name event'].strip()
        ev_id=future_events_resp[i]['id']
        if future_events_resp[i]['fields']['Свободных мест']<1:
            WL=True
        else:
            WL=False
        try:
            ev_subscrition=future_events_resp[i]['fields']['is_it_subscribers_only']
        except: ev_subscrition=False

        future_events[ev_name_w_places]=[ev_id, WL, ev_subscrition]
    return future_events


def for_feedback_events():  # вернёт словарь для ДАЧИ фидбэка {эвент без мест: евент айди}
    feedback_events_resp = airt_event.get_all(view=airt_event_tbl_for_feedback_view)
    feedback_events = {}
    for i in range(len(feedback_events_resp)):
        ev_name = feedback_events_resp[i]['fields']['Name_event'].strip()
        ev_id = feedback_events_resp[i]['id']
        feedback_events[ev_name] = ev_id
    return feedback_events


def for_reminder_events():  # вернёт словарь для напоминания {эвент без мест: евент айди}
    feedback_events_resp = airt_event.get_all(view=airt_event_tbl_open_for_reg_view)
    feedback_events = {}
    for i in range(len(feedback_events_resp)):
        ev_name = feedback_events_resp[i]['fields']['Name_event']
        ev_id = feedback_events_resp[i]['id']
        feedback_events[ev_name] = ev_id
    return feedback_events


def for_reg_event_list(username):   # вернёт 2 листа на что зареган точно, и на что зареган в ВЛ
    # получаю словарь {айди: имя}
    future_events = {}
    future_events_resp = airt_event.get_all(view=airt_event_tbl_future_events_view,
                                            fields=[airt_event_tbl_name_event_field, airt_event_tbl_time])
    for i in range(len(future_events_resp)):
        ev_date = future_events_resp[i]['fields']['Начало Мероприятия']
        ev_date=ev_date[8]+ev_date[9]+'.'+ev_date[5]+ev_date[6]
        ev_name = future_events_resp[i]['fields']['Name_event']
        ev_id = future_events_resp[i]['id']
        future_events[ev_id] = ev_date+': '+ev_name
    # получаю лист диктов из регистрации
    reg_event_list_WL=[]
    reg_event_list_R=[]
    reg_event_list_resp = airt_reg.get_all(view=airt_reg_tbl_future_events_view,
                                     fields=[airt_reg_tbl_event_for_reg_field, airt_reg_tbl_You_login_in_TG_field, airt_reg_tbl_in_wait_list_field])
    # делаю 2 списка
    if username[0]!='@':
        username = '@' + username
    username=username.lower()
    for i in range(len(reg_event_list_resp)):
        try:
            username_from_reg=reg_event_list_resp[i]['fields']['You login in TG (reg)'].lower()
        except: username_from_reg='@no_nick'
        if username_from_reg[0]!='@':
            username_from_reg='@'+username_from_reg
        if username_from_reg==username:
            try:
                in_wait_list=reg_event_list_resp[i]['fields']['in_wait_list']
            except:
                in_wait_list=False
            ev_id=reg_event_list_resp[i]['fields']['Event for reg'][0]
            ev_name=future_events[ev_id]
            if in_wait_list:
                if ev_name in reg_event_list_WL:
                    reg_event_list_WL[reg_event_list_WL.index(ev_name)]=reg_event_list_WL[reg_event_list_WL.index(ev_name)]+strs.plus_one_in_lis
                else:
                    reg_event_list_WL.append(ev_name)
            else:
                if ev_name in reg_event_list_R:
                    reg_event_list_R[reg_event_list_R.index(ev_name)]=reg_event_list_R[reg_event_list_R.index(ev_name)]+strs.plus_one_in_lis
                else:
                    reg_event_list_R.append(ev_name)
    reg_event_list_WL=list(set(reg_event_list_WL))
    reg_event_list_R=list(set(reg_event_list_R))
    reg_event_list_WL = sorted(reg_event_list_WL, key=lambda item: item[3] + item[4] + item[0] + item[1])
    reg_event_list_R = sorted(reg_event_list_R, key=lambda item: item[3] + item[4] + item[0] + item[1])
    return reg_event_list_R, reg_event_list_WL


def tgnicks_of_event_R(event_id): # вернёт лист тг ников мероприятия только чётко зареганых
    tgnicks_list=[]
    reg_event_list_resp = airt_reg.get_all(view=airt_reg_tbl_for_bot_view,
                                           fields=[airt_reg_tbl_You_login_in_TG_field, airt_reg_tbl_event_for_reg_field, airt_reg_tbl_in_wait_list_field])
    # убираю вейтлист
    for i in range(len(reg_event_list_resp)):
        try:
            if reg_event_list_resp[i]['fields']['in_wait_list']:
                reg_event_list_resp[i]['fields']['Event for reg']=['None']
        except:
            pass

    # собираю лист
    for i in range(len(reg_event_list_resp)):
        if reg_event_list_resp[i]['fields']['Event for reg']==[event_id]: #and reg_event_list_resp[i]['fields']['You login in TG (reg)'][0]=='@':
            try:
                new_nick=reg_event_list_resp[i]['fields']['You login in TG (reg)'].lower().strip()
            except:
                pass
            if new_nick[0]!='@':
                new_nick='@'+new_nick
            tgnicks_list.append(new_nick)

    return tgnicks_list

def tgnicks_of_event_R_and_WL(event_id): # вернёт лист тг ников мероприятия зареганых и в ВЛ
    tgnicks_list=[]
    reg_event_list_resp = airt_reg.get_all(view=airt_reg_tbl_for_bot_view,
                                           fields=[airt_reg_tbl_You_login_in_TG_field, airt_reg_tbl_event_for_reg_field])
    # собираю лист
    for i in range(len(reg_event_list_resp)):
        try:
            if reg_event_list_resp[i]['fields']['Event for reg']==[event_id] and reg_event_list_resp[i]['fields']['You login in TG (reg)'][0]=='@':
                tgnicks_list.append(reg_event_list_resp[i]['fields']['You login in TG (reg)'].lower())
        except:
            pass
    return tgnicks_list

def get_user_name(user_nick):
    if user_nick[0]!='@':
        user_nick='@'+user_nick
    user_nick=user_nick.lower().lstrip()
    reg_event_list_resp = airt_ppl.search(field_name=airt_ppl_tbl_tg_nick_field,
                                          field_value=user_nick)
    try:
        user_name=reg_event_list_resp[len(reg_event_list_resp)-1]['fields']['user_name']
    except:
        user_name=None
    return user_name


def get_admin_list():
    reg_event_list_resp = airt_adlist.get_all(fields=airt_adlist_tbl_name_field)
    adminlist=[]
    for i in range(len(reg_event_list_resp)):
        adminlist.append(reg_event_list_resp[i]['fields']['Name'])

    return adminlist



def for_cancel_reg_event_list(username): # вернёт дикт с айди записи и названием мероприятия
    if username[0]!='@':
        username='@'+username
    username=username.lower()
    # получаю словарь {айди: имя}
    future_events = {}
    future_events_resp = airt_event.get_all(view=airt_event_tbl_future_events_view,
                                            fields=[airt_event_tbl_name_event_field, airt_reg_tbl_cancelebl_field])
    for i in range(len(future_events_resp)):
        ev_name = future_events_resp[i]['fields']['Name_event']
        ev_id = future_events_resp[i]['id']
        cancelebl=future_events_resp[i]['fields']['cancelable']
        future_events[ev_id] = [ev_name, cancelebl]
    # получаю зиписи из рег {ev_id: rec_id}
    reg_event_list_resp = airt_reg.get_all(view=airt_reg_tbl_cancelebl_view,
                                           fields=[airt_reg_tbl_event_for_reg_field,
                                                   airt_reg_tbl_You_login_in_TG_field])
    from_reg_dickt={}
    for i in range(len(reg_event_list_resp)):
        try:
            username_from_reg=reg_event_list_resp[i]['fields']['You login in TG (reg)'].lower()
        except:
            username_from_reg='@'
        if username_from_reg[0]!='@':
            username_from_reg='@'+username_from_reg
        if username_from_reg==username:
            ev_id=' '.join(reg_event_list_resp[i]['fields']['Event for reg'])
            rec_id=reg_event_list_resp[i]['id']
            if ev_id in list(from_reg_dickt.keys()):
                from_reg_dickt[ev_id].append(rec_id)
            else:
                from_reg_dickt[ev_id]=[rec_id]

    # сливаю в {имя евента: [rec_id, rec_id, ...]}
    cancel_dickt={}
    for i in range(len(from_reg_dickt)):
        ev_id=list(from_reg_dickt.keys())[i]
        ev_name = future_events[list(from_reg_dickt.keys())[i]][0]
        rec_id = from_reg_dickt[ev_id]
        cancelebl=future_events[list(from_reg_dickt.keys())[i]][1]
        if ev_id in list(future_events.keys()):
            cancel_dickt[ev_name]=[rec_id, cancelebl]
    return cancel_dickt # {имя евента: [rec_id, rec_id, ...]}


def find_user_id_or_nick(user_nick_or_id_list):
    with open('user_names_chatid.pkl', 'rb') as f:
        user_nicks_chatid_dict = pickle.load(f)
        user_id_or_nick=[]
        for i in range(len(user_nick_or_id_list)):
            if type(user_nick_or_id_list[i])==int:
                try:
                    this_user_nick = user_nicks_chatid_dict[user_nick_or_id_list[i]].lower().strip()
                    if this_user_nick[0]!='@':
                        this_user_nick='@'+this_user_nick
                    user_id_or_nick.append(this_user_nick)
                except: pass
            else:
                this_user_nick=user_nick_or_id_list[i].lower().strip()
                if this_user_nick[0]!='@':
                    this_user_nick2='@'+this_user_nick
                else:
                    this_user_nick2=this_user_nick[1:]
                try:
                    this_user_id=user_nicks_chatid_dict[this_user_nick]
                    user_id_or_nick.append(this_user_id)
                except:
                    try:
                        this_user_id = user_nicks_chatid_dict[this_user_nick2]
                        user_id_or_nick.append(this_user_id)
                    except: pass
        f.close()
    user_id_or_nick = list(set(user_id_or_nick))
    return user_id_or_nick

def add_new_user(user_nick, user_id):
    if user_nick!=None:
        if user_nick[0]=='@':
            user_nick = '@' + user_nick
        user_nick=user_nick.lower().strip()
        with open('user_names_chatid.pkl', 'rb') as f:
            user_nicks_chatid_dict = pickle.load(f)
            try:
                user_nicks_chatid_dict[user_nick]
            except:
                user_nicks_chatid_dict[user_nick] = user_id
                user_nicks_chatid_dict[user_id] = user_nick
                with open('user_names_chatid.pkl', 'wb') as f:
                    pickle.dump(user_nicks_chatid_dict, f, pickle.HIGHEST_PROTOCOL)
            f.close()

def add_reg(for_reg_dickt): # вносит запись в регистрацию
    airt_reg.insert(
        {airt_reg_tbl_event_for_reg_field: for_reg_dickt['event_id'].split(' '),
         airt_reg_tbl_You_login_in_TG_field: for_reg_dickt['user_nick'],
         airt_reg_tbl_your_name_field: for_reg_dickt['user_name'],
         airt_reg_tbl_in_wait_list_field: for_reg_dickt['reg_in_WL']
        })
    if for_reg_dickt['plus_one']:
        airt_reg.insert({
             airt_reg_tbl_event_for_reg_field: for_reg_dickt['event_id'].split(' '),
             airt_reg_tbl_You_login_in_TG_field: for_reg_dickt['user_nick'],
             airt_reg_tbl_your_name_field: for_reg_dickt['user_name']+' +1',
             airt_reg_tbl_in_wait_list_field: for_reg_dickt['reg_in_WL']
             })
    if for_reg_dickt['first_time']:
        airt_ppl.insert({
            airt_ppl_tbl_tg_nick_field: for_reg_dickt['user_nick'],
            airt_ppl_tbl_user_name_field: for_reg_dickt['user_name']
            })

    airt_resp=airt_reg.get_all(view=airt_reg_tbl_for_bot_view,
                     fields=[airt_reg_tbl_You_login_in_TG_field, airt_reg_tbl_event_for_reg_field])
    reg_check=[]
    for i in range(len(airt_resp)):
        try:
            if airt_resp[i]['fields']['You login in TG (reg)']==for_reg_dickt['user_nick']:
                reg_check.append(airt_resp[i]['fields']['Event for reg'])
        except: pass
    if for_reg_dickt['event_id'].split(" ") in reg_check:
        success = True
    else:
        success = False
    return success

def add_feedback(feedback_dickt):
    rec={
                          airt_feedback_tbl_name_event_field: feedback_dickt['event_id'].split(' '),
                          airt_feedback_tbl_you_login_in_TG_field: feedback_dickt['user_nick'],
                          airt_feedback_tbl_what_did_you_like_field: feedback_dickt['what_did_you_like'],
                          airt_feedback_tbl_lishnee_field: feedback_dickt['unwanted'],
                          airt_feedback_tbl_comment_field: feedback_dickt['comment'],
                          airt_feedback_tbl_whats_your_name_field: feedback_dickt['user_name'],
                          }
    if feedback_dickt['recomendacion']!=0:
        rec[airt_feedback_tbl_recomendacion_field]=feedback_dickt['recomendacion']
    airt_feedback.insert(rec)


def del_registration(rec_list):
    deleted=airt_reg.batch_delete(rec_list)[0]['deleted']
    return deleted

def get_all_id():
    with open('user_names_chatid.pkl', 'rb') as f:
        user_nicks_chatid_dict = list(pickle.load(f).keys())
        all_user_id=[]
        for i in range(len(user_nicks_chatid_dict)):
            if type(user_nicks_chatid_dict[i]) is int:
                all_user_id.append(user_nicks_chatid_dict[i])
    return all_user_id

