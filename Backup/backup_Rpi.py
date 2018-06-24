import os 
import sys
import datetime

base_path = '/home/pi/RPi_Backups/'
backup_list = ''
backup_file = ''
backup_list_full = ['/home', '/etc', '/sys', '/lib', '/srv', '/sbin', '/bin', '/var', '/media', '/selinux', '/usr', '/opt']
#backup_list_partial = ['/home', '/etc']

backup_file = base_path + 'full_' + datetime.datetime.now().strftime('%m%d%y') + '.tar.gz'
backup_list = backup_list_full

os.system('rm -f full_*')


os.system('tar cvfz ' + backup_file + ' ' + ' '.join(backup_list))
