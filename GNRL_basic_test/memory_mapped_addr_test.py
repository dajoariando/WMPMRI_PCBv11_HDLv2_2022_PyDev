#!/usr/bin/python

import pydevd
import mmap
import time

from pydevd_file_utils import setup_client_server_paths

# PATH_TRANSLATION = [
#    ('D:\\GDrive\\WORKSPACES\\Eclipse_Python_2018\\RemoteSystemsTempFiles\\DAJO-DE1SOC\\root\\Eclipse_Python_2018\\GNRL_basic_test\\',
#     '/root/Eclipse_Python_2018/GNRL_basic_test/')
#]

# ip addresses settings for the system
server_ip = '129.22.143.88'
client_ip = '129.22.143.39'
server_path = '/root/nmr_pcb20_hdl10_2018/GNRL_basic_test/'
# client path with samba
client_path = 'X:\\nmr_pcb20_hdl10_2018\\GNRL_basic_test\\'

# setup_client_server_paths(PATH_TRANSLATION)
# pydevd.settrace("dajo-compaqsff")

from pydevd_file_utils import setup_client_server_paths
PATH_TRANSLATION = [(client_path, server_path)]
setup_client_server_paths(PATH_TRANSLATION)
print("---server:%s---client:%s---" %
      (server_ip, client_ip))
pydevd.settrace(client_ip, stdoutToServer=True,
                stderrToServer=True)

# static addresses of the FPGA
h2f_axi_master_span = 0x40000000
h2f_axi_master_ofst = 0xC0000000
h2f_lwaxi_master_span = 0x200000
h2f_lwaxi_master_ofst = 0xff200000

# axi defined addresses
h2f_switch_addr_ofst = 0x4000000
# lwaxi defined addresses
h2f_dconv_addr_ofst = 0x0448
h2f_dconvq_addr_ofst = 0x04c0
h2f_NoP_addr_ofst = 0x0010

# BASIC LED test
perform_basic_led_test = False
if perform_basic_led_test:
    with open("/dev/mem", "r+") as f:
        # memory-map the file, size 0 means whole file
        mem = mmap.mmap(f.fileno(), h2f_axi_master_span,
                        offset=h2f_axi_master_ofst)

        while 1:
            mem.seek(h2f_switch_addr_ofst)
            data = mem.read(4)  # read the data in byte format
            dataint = int.from_bytes(data, byteorder='little')
            time.sleep(0.5)
            print("current data = %d" % dataint)

        mem.close()  # close the map

# read from memory
with open("/dev/mem", "r+") as f:
    # memory-map the file, size 0 means whole file
    mem = mmap.mmap(f.fileno(), h2f_lwaxi_master_span,
                    offset=h2f_lwaxi_master_ofst)

    while 1:
        mem.seek(h2f_dconvq_addr_ofst)
        data = mem.read(4)  # read the data in byte format
        dataint = int.from_bytes(data, byteorder='little')
        time.sleep(0.5)
        print("current data = %d" % dataint)

    mem.close()  # close the map