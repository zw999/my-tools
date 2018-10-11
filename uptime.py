from datetime import datetime
import subprocess
import re


def human_time(tt):
    tt=float(tt)
    if tt < 60:
        return '0 min'
    elif tt < 60 * 60:
        return '%d min' % (tt//60)
    elif tt < 60 * 60 * 24:
        shi, fen = divmod(tt, 3600)
        return '%2d:%02d' % (shi,fen//60)
    elif tt >= 60 * 60 * 24:
        day,miao=divmod(tt,3600*24)
        return '%d day, %s' % (day,human_time(miao))
    else:
        return '0 min'


def get_uptime():
    '''
    $ cat /proc/uptime
    4641.64 16391.39
    :return:  1:17
    '''
    with open('/proc/uptime') as f_uptime:
        up_t=f_uptime.read().split(' ')[0]
        return human_time(up_t)

def now_time():
    now=datetime.now()
    return now.strftime('%H:%M:%S')

def get_user_count():
    '''
    :return: 已登陆用户数
    '''
    user_c=0
    numU=subprocess.run('utmpdump  /var/run/utmp',shell=True,stdout=subprocess.PIPE,stderr=subprocess.DEVNULL).stdout.decode()
    #从/var/run/utmp中读出已登陆用户信息
    #[7]是已登陆的表示

    for line in numU.splitlines():
        if re.match('^\[7\]',line):
            user_c +=1
    return user_c

def get_loadavg():
    '''
    $ cat /proc/loadavg
    1.07 0.69 0.62 1/503 4864
    '''
    with open('/proc/loadavg') as f_lavg:
        return ', '.join(f_lavg.readline().split()[0:3])

def uptime():
    nU=get_user_count()
    if nU >1:
        return now_time() + ' up ' + get_uptime() + ', %2d' % get_user_count() + ' users,  load average: ' + get_loadavg()
    else:
        return now_time()+' up '+get_uptime()+', %2d' % get_user_count()+' user,  load average: '+get_loadavg()


if __name__=='__main__':
    print(' '+uptime())
    # get_uptime()
