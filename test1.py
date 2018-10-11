def seconds2time(tt):
    minuts=int(tt//60)
    seconds=int(tt-minuts*60.0)
    hs=int((tt-minuts*60.0-seconds)*100)
    return '%d:%02d.%02d' % (minuts,seconds,hs)

print(seconds2time(98542))