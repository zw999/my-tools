from uptime import uptime
from sar import get_useage
from free import meminfo
import glob
import time
import os

class proc(object):
    def __init__(self,pidf,sleep_time=1):
        '''
        :param pidf: '/proc/1','/proc/2'
        :param sleep_time: 秒数
        '''
        self.statf = str(pidf)+'/stat'
        self.statmf = str(pidf)+'/statm'
        self._dirstat = os.stat(pidf)
        self.sleep_time=sleep_time

    def _open_statf(self):
        with open(self.statf) as _f:
            return _f.read().split()

    def _get_shrm(self):
        with open(self.statmf) as _fm:
            return _fm.read().strip().split()[2]

    def get_data(self):
        _pre_ttime=''
        __pgsize=os.sysconf('SC_PAGESIZE')
        # page size 一般是4096

        while True:
            datas=self._open_statf()
            # print(datas)
            pid,cmd,state,*_=datas
            utime=datas[13]
            stime=datas[14]
            prv=datas[17]
            nice=datas[18]
            vsize=datas[22]
            rss=datas[23]

            _total_time=int(stime) + int(utime)

            if _pre_ttime=='':
                _pre_ttime = _total_time
                continue


            cpuusage=round((_total_time-_pre_ttime)/(self.sleep_time*100)*100,1)
            # 使用cpu的时间，除以整个sleep time时间，可得到使用率。
            # sysconf(_SC_CLK_TCK) 一般是100，每秒时钟周期
            #第二个100是百分号用的

            virt=int(vsize) // 1024
            res=int(rss) * __pgsize
            shr=int(self._get_shrm()) * __pgsize

            yield [pid, str(self._dirstat.st_uid), prv, nice, virt,res, shr, state, cpuusage, _total_time, cmd]

            #pid,uid,prv,nice,virt,res,shr,state,cpuusage,runtime,cmd

            _pre_ttime=_total_time


def uid_username():
    '''
    :return: {'0':'root','1000':'cc'...}
    '''
    d_uid={}
    with open('/etc/passwd') as pwdf:
        for line in pwdf.readlines():
            line=line.strip().split(':')
            uname,_,uid,*_=line
            d_uid[uid]=uname
    return d_uid

def get_all_pids(sleep_time=1):
    '''
    :return: {'/proc/1':proc(1),'/proc/2':proc(2),...}
    '''
    d_pid={}
    pidlist=glob.glob('/proc/[1-9]*')
    for _pid in pidlist:
        d_pid[_pid]=proc(_pid,sleep_time).get_data()
    return d_pid

def update_dpid(p_old,sleep_time=1):
    '''
    glob结果 对比 已经在字典里的键，更新字典
    :param p_old: {'/proc/1':proc(1),'/proc/2':proc(2),...}
    :return: p_old
    '''
    pidlist = glob.glob('/proc/[1-9]*')
    new_p=set(pidlist).difference(set(p_old.keys()))
    del_p=set(p_old.keys()).difference(pidlist)

    if len(new_p) >0:
        for i in new_p:
            p_old[i]=proc(i,sleep_time).get_data()
    if len(del_p) > 0:
        for i in del_p:
            del p_old[i]

def seconds2time(tt):
    minuts=int(tt//60)
    seconds=int(tt-minuts*60.0)
    hs=int((tt-minuts*60.0-seconds)*100)
    return '%d:%02d.%02d' % (minuts,seconds,hs)


if __name__=='__main__':

    sleep_time=1
    d_uid=uid_username()
    cpudata = get_useage(float_j=1)
    p_old=get_all_pids(sleep_time)

    os.system('clear')
    while True:
        update_dpid(p_old, sleep_time)
        top_data = list(map(lambda x: next(x), p_old.values()))

        #cpu
        cpu_user, cpu_nice, cpu_sys, cpu_idle, cpu_iow, cpu_irq, cpu_sirq, cpu_st, cpu_guest = next(cpudata)
        cdata=(cpu_user,cpu_sys,cpu_nice,cpu_idle,cpu_iow,cpu_irq,cpu_sirq,cpu_st)

        #mem
        dd = meminfo()
        buff_cache = dd['Buffers'] + dd['Cached'] + dd['Slab']
        used = dd['MemTotal'] - dd['MemFree'] - buff_cache

        #Tasks
        p_status = [x[7] for x in top_data]

        print('top -',uptime())
        print('Tasks: \033[1m%d\033[0m total,   \033[1m%d\033[0m running, \033[1m%d\033[0m sleeping,   \033[1m%d\033[0m stopped,   \033[1m%d\033[0m zombie' % (len(p_status),p_status.count('R'),p_status.count('S'),p_status.count('T'),p_status.count('Z')))
        print('%%Cpu(s):\033[1m%5.1f\033[0m us,\033[1m%5.1f\033[0m sy,\033[1m%5.1f\033[0m ni,\033[1m%5.1f\033[0m id,\033[1m%5.1f\033[0m wa,\033[1m%5.1f\033[0m hi,\033[1m%5.1f\033[0m si,\033[1m%5.1f\033[0m st' % cdata)
        print('KiB Mem : \033[1m%d \033[0mtotal, \033[1m%d \033[0mfree,  \033[1m%d \033[0mused,  \033[1m%d \033[0mbuff/cache' % (dd['MemTotal'],dd['MemFree'],used,buff_cache))
        print('KiB Swap:  \033[1m%d \033[0mtotal,  \033[1m%d \033[0mfree,        \033[1m%d \033[0mused. \033[1m%d \033[0mavail Mem' % (dd['SwapTotal'],dd['SwapFree'],dd['SwapTotal'] - dd['SwapFree'],dd['MemAvailable']))

        #proc
        print('\033[30;47m  PID USER      PR  NI    VIRT    RES    SHR S  %CPU %MEM     TIME+ COMMAND\033[0m')

        _sort_list=sorted(top_data,key=lambda process:process[8],reverse=True)[:21]
        for i in _sort_list:
            pid, uid, prv, nice, virt, res, shr, state, cpuusage, runtime, cmd =i

            #处理输出格式，过长的变为xxxg
            new_res=res//1024
            if len(str(new_res)) > 6:
                new_res=new_res/1024/1024
                new_res='%5.3fg' % new_res
            else:
                new_res='%6d' % new_res
            #
            if prv == '-100':
                prv='rt'
            #python的进程加粗
            if  'python' in cmd:
                print('\033[1m',end='')
            print('%5s %-7s %4s %3s %7d %6s %6d %1s %5.1f %4.1f %9s %-15s' % (pid,d_uid[uid],prv,nice,virt,new_res,shr/1024,state,cpuusage,round(res/1024/dd['MemTotal']*100,1),seconds2time(runtime/100),cmd[1:-1]))
            print('\033[0m',end='')

        time.sleep(sleep_time)
        os.system('clear')

