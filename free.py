import sys

def human_readable(plain_size):
    '''

    :param plain_size: 数字大小
    :return: 人类可读的大小
    '''
    plain_size = float(plain_size)
    if plain_size <= 1024:
        return str( round(plain_size, 1)) + 'K'
    if plain_size <= 1024 * 1024:
        return str( round(plain_size / 1024, 1)) + 'M'
    if plain_size <= 1024 * 1024 * 1024:
        return str( round(plain_size / 1024 / 1024, 1)) + 'G'


def free_print(dd={},flag=0):
    '''
    :param dd: 内存信息列表
    :param flag: -m, -g
    '''
    buff_cache=dd['Buffers'] + dd['Cached'] + dd['Slab']
    used=dd['MemTotal'] - dd['MemFree'] - buff_cache
    mem_data=(dd['MemTotal'], used, dd['MemFree'], dd['Shmem'], buff_cache, dd['MemAvailable'])
    swap_data = (dd['SwapTotal'], dd['SwapTotal'] - dd['SwapFree'], dd['SwapFree'])


    print('              total        used        free      shared  buff/cache   available')
    if flag==0:
        print('MEM:   %12s%12s%12s%12s%12s%12s' % tuple(map(human_readable, mem_data)))
        print('SWAP:  %12s%12s%12s' % tuple(map(human_readable, swap_data)))
    else:
        print('MEM:   %12d%12d%12d%12d%12d%12d' % tuple(map(lambda x:x/flag, mem_data)))
        print('SWAP:  %12d%12d%12d' % tuple(map(lambda x: x / flag, swap_data)))


def meminfo():
    '''
    :return: {'MemTotal':'16314516',...}
    '''
    with open('/proc/meminfo') as f:
        dd={}
        for i in f.read().splitlines():
            k,v=i.split(':')
            dd[k]=int(v.strip().split(' ')[0])
    return dd

def check_args(opts):
    flag=0
    if len(opts) > 0:
        for opt in opts:
            if opt == '-m':
                flag = 1024
            elif opt == '-g':
                flag = 1024 * 1024
            elif opt == '-h':
                flag = 0
            else:
                print('''
    Usage: python3 free.py [OPTION]
    options:
        -m, MB
        -g, GB
        -h, human
    ''')
                sys.exit(1)
    return flag

if __name__ == '__main__':
    free_print(meminfo(), check_args(sys.argv[1:]))