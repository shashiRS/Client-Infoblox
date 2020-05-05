import os
import re
import config
import pytest
import unittest
import logging
import subprocess
import paramiko
import json
import shlex
from time import sleep
from subprocess import Popen, PIPE
import ib_utils.ib_NIOS as ib_NIOS
#from ib_utils.log_capture import log_action as log
#logging.basicConfig(format='%(asctime)s - %(name)s(%(process)d) - %(levelname)s - %(message)s',filename="niosspt_8743.log" ,level=logging.DEBUG,filemode='w')

class NIOSSPT_10043(unittest.TestCase):

    @pytest.mark.run(order=1)
    def test_001_validate_MTU(self):
        print(" Validating message")
        args = "sshpass -p 'infoblox' ssh -o StrictHostKeyChecking=no admin@"+config.grid_vip
        args=shlex.split(args)
        child = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        data="lan2 1302"
        child.stdin.write("set interface_mtu "+data+" \n")
    
        output = child.communicate()
        msg="Failed to set MTU"
        
        for line in list(output):
	    if 'Disconnect NOW if you have' in line:
               continue
            if msg in line:
               print("Sucess: Found the message")
               print(msg)
               assert True
              
            else:
               print("Unsucsess: Could not found the message")
               print(msg)
               assert False
        

        #validate_message()
    @pytest.mark.run(order=2)
    def test_002_enable_port_redundancy(self):
        print("Enable port redundancy on LAN1/LAN2")
        get_ref = ib_NIOS.wapi_request('GET', object_type='member')
        data = {"lan2_port_setting":{"enabled":True, "nic_failover_enable_primary":True,"nic_failover_enabled":True}}
        for ref in json.loads(get_ref):
            response = ib_NIOS.wapi_request('PUT', ref=json.loads(get_ref)[0]['_ref'], fields=json.dumps(data))
            print(response)
            if type(response) == tuple:
                if response[0]==400 or response[0]==401:
                    print("Failure: Enable port redundancy on LAN1/LAN2")
                    assert False
                else:
                    print("Success: Enable port redundancy on LAN1/LAN2")
                    sleep(300)
                    assert True
                    
                    
    
        
        
    @pytest.mark.run(order=3)
    def test_003_port_redundancy_validate(self):
        print(" Validating message port redundancy")
        sleep(300)
        args = "sshpass -p 'infoblox' ssh -o StrictHostKeyChecking=no admin@"+config.grid_vip
        args=shlex.split(args)
        child = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        data="lan2 1302"
        child.stdin.write("set interface_mtu "+data+" \n")
        #child.stdin.write("exit")
        output = child.communicate()
        msg="MTU Value of lan2 cannot be set when port redundancy is enabled"
        #print(output)
        for line in list(output):
          
            if 'Disconnect NOW if you have' in line:
                continue
            if msg in line:
                print("Sucessfully Found the message")
                print(msg)
                assert True
            else:
                print("Unsucsessful")
                print(msg)
                assert False
     
     
    @pytest.mark.run(order=4)
    def test_004_port_redundancy_validate1(self):
        print(" Validating message port redundancy")
        sleep(5)
        args = "sshpass -p 'infoblox' ssh -o StrictHostKeyChecking=no admin@"+config.grid_vip
        args=shlex.split(args)
        child = Popen(args, stdin=PIPE, stdout=PIPE, stderr=PIPE)
        data="lan 1302"
        child.stdin.write("set interface_mtu "+data+" \n")
      
        output = child.communicate()
        msg="MTU Value of lan cannot be set when port redundancy is enabled"

        for line in list(output):
            if 'Disconnect NOW if you have' in line:
                continue
            if msg in line:
                print("Sucessfully Found the message")
                print(msg)
                assert True
            else:
                print("Unsucsessful")
                print(msg)
                assert False
                
                
                
    
     
