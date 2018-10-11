import time
from datetime import datetime


def get_cpu(c):
    '''以列表形式返回/proc/stat中的数据
    参数：
        c： cpu编号， ‘cpu’代表所有，cpu0表示第一个cpu

    数据：
        cpu  79918 158 11007 799127 540 0 1016 0 0 0
        cpu0 20152 12 2564 200032 50 0 217 0 0 0
        cpu1 19984 15 2369 200448 140 0 243 0 0 0
        cpu2 20141 13 3254 198885 289 0 416 0 0 0
        cpu3 19639 116 2819 199760 60 0 139 0 0 0

    '''
    with open('/proc/stat') as f_stat:
        while True:
            line=f_stat.readline()
            if c+' ' in line:
                return line.strip().split()


def get_useage(c='cpu',float_j=2):
    '''
    :param c: cpu编号， ‘cpu’代表所有，cpu0表示第一个cpu
    :param float_j: 浮点数精度，1就是1位小数
    :return:
    '''

    old_data=[c]
    old_data.extend([0]*10)
    #创建一个旧数据，初始化为0

    while True:
        _tmp_cdata=get_cpu(c)
        cdata=[_tmp_cdata[0]]
        cdata.extend(map(int,_tmp_cdata[1:]))
        #cpu  79918 158 11007 799127 540 0 1016 0 0 0

        cpu_sum = sum(cdata[1:])
        cpu_delta = cpu_sum - sum(old_data[1:])

        tmp_l=[]
        for i in range(1,10):
            tmp_l.append(round((cdata[i]-old_data[i])/cpu_delta*100,float_j))
        #逐个相减并计算百分比
        #cpu_user, cpu_nice, cpu_sys, cpu_idle, cpu_iow, cpu_irq, cpu_sirq, cpu_st, cpu_guest = tmp_l

        yield tmp_l
        old_data = cdata


if __name__=='__main__':
    cc=get_useage()
    i = 1
    #i是控制输出行数的
    while True:
        cpu_user, cpu_nice, cpu_sys, cpu_idle, cpu_iow, cpu_irq, cpu_sirq, cpu_st, cpu_guest=next(cc)

        n_time=datetime.now().strftime('%H:%M:%S')

        if i==1:
            print(n_time,'     CPU     %user     %nice   %system   %iowait    %steal     %idle')
        data=(cpu_user,cpu_nice,cpu_sys,cpu_iow,cpu_st,cpu_idle)
        print(n_time,'     all','%10.2f%10.2f%10.2f%10.2f%10.2f%10.2f' % data)

        i+=1
        if i==11:
            i=1
        time.sleep(1)
