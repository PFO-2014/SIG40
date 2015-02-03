'''
Created on 23 juil. 2014

@author: http://ubuntuforums.org/showthread.php?t=1215042
'''


def get_ip_address():
    """
    @author: http://ubuntuforums.org/showthread.php?t=1215042
    """
    import socket
#=========================================================================
# 1: Use the gethostname method
#
#     ipaddr = socket.gethostbyname(socket.gethostname())
#     if not(ipaddr.startswith('127')):
#         print('Can use Method 1: ' + ipaddr)
# return ipaddr
#
# 2: Use outside connection
#     '''
#     Source:
#     http://commandline.org.uk/python/how-to-find-out-ip-address-in-python/
#     '''
#
#     ipaddr = ''
#     s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#     try:
#         s.connect(('google.com', 0))
#         ipaddr = s.getsockname()[0]
#         print('Can used Method 2: ' + ipaddr)
# return ipaddr
#     except:
#         pass
#=========================================================================

    # 3: Use OS specific command
    import subprocess
    import platform
    ipaddr = ''
    os_str = platform.system().upper()
    try:
        if os_str == 'LINUX':

            # Linux:
            arg = 'ip route list'
            p = subprocess.Popen(arg, shell=True, stdout=subprocess.PIPE)
            data = p.communicate()
            sdata = data[0].split()
            ipaddr = sdata[sdata.index('src') + 1]
            #netdev = sdata[ sdata.index('dev')+1 ]
            #print('Can used Method 3: ' + ipaddr)
            return ipaddr

        elif os_str == 'WINDOWS':

            # Windows:
            arg = 'route print 0.0.0.0'
            p = subprocess.Popen(arg, shell=True, stdout=subprocess.PIPE)
            data = p.communicate()
            strdata = data[0].decode()
            sdata = strdata.split()

            while len(sdata) > 0:
                if sdata.pop(0) == 'Netmask':
                    if sdata[0] == 'Gateway' and sdata[1] == 'Interface':
                        ipaddr = sdata[6]
                        break
            #print('Can used Method 4: ' + ipaddr)
            return ipaddr
    except:
        return "Adresse IP inconnue"
