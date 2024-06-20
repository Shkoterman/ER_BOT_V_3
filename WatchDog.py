import PySimpleGUI as psg
import time
import asyncio

check_time = 3
first_check_delay = 1500
tries = 3
restart_timer = 10

connection_ok_msg = 'OK'
connection_lost_msg = 'lost!'
restart_msg = 'Asking restart'
waiting_msg = 'waiting for first check'

def check_connection(tries):


    return False

async def countdown():
    await asyncio.sleep(1)
    print(123)

layout = [  [psg.Text('Connection ... ')], [psg.Text(waiting_msg, key='connection_status')],
            [psg.Text('On watch', key='acton')],
            [psg.Button('Cancel'), psg.Button('Test')]]

window = psg.Window('WatchDog', layout)
chexk = window.timer_start(first_check_delay, 'check_time', True)


while True:


        event, values = window.read()

        if event=='check_time':
            connection_status=check_connection(tries)

            if connection_status==False:
                window.timer_stop(chexk)
                countdown()
                restart=psg.popup_yes_no('Connection faild!\nRestart in 60 sec', title ='Restart', auto_close=True, auto_close_duration=restart_timer, modal=False)

                if restart=='Yes':
                    restart=True
                    window['acton'].update('Restarting')
                else:
                    restart=False
                    window['acton'].update('WatchDog was stoped')
            else: print(567567)
            window['connection_status'].update(connection_status)

        elif event == 'countdown':
            print(123)
        elif event == psg.WIN_CLOSED or event == 'Cancel':
            break





window.close()
