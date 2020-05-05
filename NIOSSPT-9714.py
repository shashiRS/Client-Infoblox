#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = "Shashikala R S"
__email__  = "srs@infoblox.com"

#############################################################################
#  Grid Set up required:                                                    #
#  1. Licenses : DNS(enabled), DHCP, Grid                                   #
#############################################################################
import os
import re
import config
import pytest
import unittest
import logging
import json
from time import sleep
import ib_utils.ib_NIOS as ib_NIOS
import pexpect

class NIOSSPT_9714(unittest.TestCase):

    @pytest.mark.run(order=1)
    def test_000_start_IPv4_DHCP_service(self):
        print("Enable the DPCH service")
        get_ref = ib_NIOS.wapi_request('GET', object_type="member:dhcpproperties?_return_fields=enable_dhcp", grid_vip=config.grid_vip)
        print(get_ref)
        ref = json.loads(get_ref)[0]['_ref']
        data = {"enable_dhcp":True}
        response = ib_NIOS.wapi_request('PUT',ref=ref,fields=json.dumps(data), grid_vip=config.grid_vip)
        print(response)
    
    
    @pytest.mark.run(order=2)
    def test_001_create_New_AuthZone(self):
        print("Create A new Zone")
      
        data = {"fqdn": "test.com","grid_primary": [{"name": config.grid_member1_fqdn,"stealth":False}, {"name": config.grid_member2_fqdn,"stealth":False}]}
        response = ib_NIOS.wapi_request('POST', object_type="zone_auth", fields=json.dumps(data))
        print response
        
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Create A new Zone")
                assert False
            else:
                print("Success: Create A new Zone")
                assert True
     
        print("Restart DHCP Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(20)
                   
    @pytest.mark.run(order=3)
    def test_002_add_a_DTC_Server1(self):
        logging.info("Create A DTC first Server")
        data = {"name":"server1","host":"10.35.118.2"}
        response = ib_NIOS.wapi_request('POST', object_type="dtc:server", fields=json.dumps(data))
        print response
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Create A DTC first Server")
                assert False
            else:
                print("Success: Create A DTC first Server")
                assert True
    
    @pytest.mark.run(order=4)
    def test_003_add_a_DTC_Server2(self):
        logging.info("Create A DTC second Server")
        data = {"name":"server2","host":"10.36.198.3"}
        response = ib_NIOS.wapi_request('POST', object_type="dtc:server", fields=json.dumps(data))
        print response
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Create A DTC second Server")
                assert False
            else:
                print("Success: Create A DTC second Server")
                assert True
                
    # @pytest.mark.run(order=5)
    # def test_004_add_a_DTC_Server3(self):
        # logging.info("Create A DTC third Server")
        # data = {"name":"server2","host":"10.120.21.222"}
        # response = ib_NIOS.wapi_request('POST', object_type="dtc:server", fields=json.dumps(data))
        # print response
        # if type(response) == tuple:
            # if response[0]==400 or response[0]==401:
                # print("Failure: Create A DTC third Server")
                # assert False
            # else:
                # print("Success: Create A DTC third Server")
                # assert True
                
                
                
                
    # @pytest.mark.run(order=6)
    # def test_005_add_a_DTC_Server4(self):
        # print("Create A DTC fourth Server")
        # data = {"name":"server2","host":"10.120.21.223"}
        # response = ib_NIOS.wapi_request('POST', object_type="dtc:server", fields=json.dumps(data))
        # print response
        # if type(response) == tuple:
            # if response[0]==400 or response[0]==401:
                # print("Failure: Create A DTC fourth Server")
                # assert False
            # else:
                # print("Success: Create A DTC fourth Server")
                # assert True
        
        
        
    @pytest.mark.run(order=7)
    def test_006_add_a_DTC_pool(self):
        print("Create A DTC Pool and add servers in it")
        get_ref = ib_NIOS.wapi_request('GET', object_type="dtc:server", grid_vip=config.grid_vip)
        index=1
        serv=[]
        for ref in json.loads(get_ref):
            if 'server1' in ref['_ref']:   
                serv.append({"ratio":index ,"server": ref['_ref']})
                index=index+1
            if 'server2' in ref['_ref']:   
                serv.append({"ratio":index ,"server": ref['_ref']})
                index=index+1
        #print(serv)            
        
        get_ref = ib_NIOS.wapi_request('GET', object_type="dtc:monitor:http", grid_vip=config.grid_vip)
        monitor=[]
        for ref in json.loads(get_ref):
            if not'https' in ref['_ref']:
                monitor.append(ref['_ref'])
        print(monitor)
        data = {"name":"pool_p","lb_preferred_method":"ROUND_ROBIN","servers": serv,"monitors":monitor}
        response = ib_NIOS.wapi_request('POST', object_type="dtc:pool", fields=json.dumps(data))
        print(response)
        
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Create A DTC Pool and add servers in it")
                assert False
            else:
                print("Success: Create A DTC Pool and add servers in it")
                assert True
    
    
        
    @pytest.mark.run(order=8)
    def test_007_add_a_DTC_lbdn(self):
        print("Create A DTC LBDN")
        #get_ref_topo = ib_NIOS.wapi_request('GET', object_type="dtc:topology", grid_vip=config.grid_vip)
        
        get_ref_pool = ib_NIOS.wapi_request('GET', object_type="dtc:pool", grid_vip=config.grid_vip)
        pool_lst=[]
        ind=1
        for ref in json.loads(get_ref_pool):
            print(ref['_ref'])
            if 'pool_p' in ref['_ref']:
                pool_lst.append({"pool":ref['_ref'],"ratio":ind})
                ind=ind+1
                
        get_ref_zones = ib_NIOS.wapi_request('GET', object_type="zone_auth", grid_vip=config.grid_vip)
        zone_lst=[]
        for ref in json.loads(get_ref_zones):
            print(ref['_ref'])
            if 'test.com' in ref['_ref']:
                zone_lst.append(ref['_ref'])
                       
        print(pool_lst,zone_lst)   
        data = {"name":"lbdn_l","lb_method":"ROUND_ROBIN","patterns": ["arec.test.com"], "pools": pool_lst, "auth_zones":zone_lst,"types":["A","AAAA","CNAME","NAPTR"]}
        response = ib_NIOS.wapi_request('POST', object_type="dtc:lbdn", fields=json.dumps(data))
        print response
        if type(response) == tuple:
            if response[0]==400 or response[0]==401:
                print("Failure: Create A DTC LBDN")
                assert False
            else:
                print("Success: Create A DTC LBDN")
                assert True
        
        print("Restart DHCP Services")
        grid =  ib_NIOS.wapi_request('GET', object_type="grid", grid_vip=config.grid_vip)
        ref = json.loads(grid)[0]['_ref']
        data= {"member_order" : "SIMULTANEOUSLY","restart_option":"FORCE_RESTART","service_option": "ALL"}
        request_restart = ib_NIOS.wapi_request('POST', object_type = ref + "?_function=restartservices",fields=json.dumps(data),grid_vip=config.grid_vip)
        sleep(20)
        
        
    
    @pytest.mark.run(order=9)
    def test_008_assign_servers_to_pool_monitor(self):
        print("Assign_servers_to_pool_monitor")   
        get_ref = ib_NIOS.wapi_request('GET', object_type="dtc:monitor:http", grid_vip=config.grid_vip)
        monitor=""
        for ref in json.loads(get_ref):
            if not'https' in ref['_ref']:
                monitor=ref['_ref']
            
        get_ref_mem = ib_NIOS.wapi_request('GET', object_type="member", grid_vip=config.grid_vip)

        memb=[]
        ind=1
        for ref in json.loads(get_ref_mem):
            if config.grid_member1_fqdn in ref['_ref']:  
                memb.append(config.grid_member1_fqdn)
            # if config.grid_member2_fqdn in ref['_ref']:
                # memb.append(config.grid_member2_fqdn)
                
        get_ref_pool = ib_NIOS.wapi_request('GET', object_type="dtc:pool", grid_vip=config.grid_vip)
        print(get_ref_pool)
        print(memb)
        for ref in json.loads(get_ref_pool):
            if 'pool_p' in ref['_ref']:
                get_ref = ib_NIOS.wapi_request('GET', object_type=ref['_ref']+"?_return_fields=consolidated_monitors")
                data = {"consolidated_monitors": [{"availability": "ALL","members": memb,"monitor": monitor}]}
                response = ib_NIOS.wapi_request('PUT',ref=ref['_ref'], fields=json.dumps(data))
                print(response)
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401:
                        print("Failure: Assign_servers_to_pool_monitor")
                        assert False
                    else:
                        print("Success: Assign_servers_to_pool_monitor")
                        assert True
        
    @pytest.mark.run(order=10)
    def test_009_query_for_member_selected_in_pool(self):
        print("Query_for_member_selected_in_pool")
        #for i in {1..10}; do dig @10.35.169.10 arec.test.com a; sleep 1 ; done
        output = os.popen("for i in {1..10}; do dig @"+config.grid_member3_vip+" arec.test.com a; sleep 1 ; done").read()
        output = output.split('\n')
        #print(output)
        server1_found= False
        server2_found= False
        for index,value in enumerate(output):
            if 'ANSWER SECTION:' in value:
                print(output[index+1])
                print("--------------------")
                match = re.match("arec.test.com.\s+\d+\s+IN\s+A\s+10.35.118.2", output[index+1])
                match1= re.match("arec.test.com.\s+\d+\s+IN\s+A\s+10.36.198.3", output[index+1]) 
                if match:
                    server1_found = True
                    
                if match1:
                    server2_found = True
                    
                    
        if server1_found and server2_found ==True:
            print("Success: Perform dig query")
            assert True
        else:
            print("Failed: Perform dig query")
            print(output)
            assert False
        
    @pytest.mark.run(order=11)
    def test_010_Both_Server_appears_in_GREEN(self):
        print("Server1 appears in GREEN, Server2 in GREEN")
        
        get_ref = ib_NIOS.wapi_request('GET', object_type="dtc:server?_return_fields=health", grid_vip=config.grid_vip)
        print(get_ref)
        for ref in json.loads(get_ref):
            if 'server1' in ref['_ref']:
               
                print("Server1:Color="+ref['health']['availability']+" Server1:Status="+ref['health']['enabled_state'])
            if 'server2' in ref['_ref']:
               
                print("Server2:Color="+ref['health']['availability']+" Server2:Status="+ref['health']['enabled_state'])
                    
    @pytest.mark.run(order=11)
    def test_010_Server1_is_up_Server2_is_down(self):
        print("Server1_is_up_Server2_is_down")
        
        get_ref = ib_NIOS.wapi_request('GET', object_type="dtc:server?_return_fields=health,disable", grid_vip=config.grid_vip)
        print(get_ref)
        for ref in json.loads(get_ref):
            if 'server1' in ref['_ref']:
               
                print("Server1:Color="+ref['health']['availability']+" Server1:Status="+ref['health']['enabled_state'])
                
                data = {"health": {"availability":"RED","enabled_state":"Error"}}
                response = ib_NIOS.wapi_request('PUT',ref=ref['_ref'], fields=json.dumps(data))
                print(response)
                if type(response) == tuple:
                    if response[0]==400 or response[0]==401:
                        print("Failure: Server1_is_up_Server2_is_down")
                        assert False
                    else:
                        print("Success: Server1_is_up_Server2_is_down")
                        assert True
        
        
        
    @pytest.mark.run(order=10)
    def test_009_query_for_member_selected_in_pool(self):
        print("Query_for_member_selected_in_pool")
        #for i in {1..10}; do dig @10.35.169.10 arec.test.com a; sleep 1 ; done
        output = os.popen("for i in {1..10}; do dig @"+config.grid_member3_vip+" arec.test.com a; sleep 1 ; done").read()
        output = output.split('\n')
        #print(output)
        server1_found= False
        server2_found= False
        for index,value in enumerate(output):
            if 'ANSWER SECTION:' in value:
                print(output[index+1])
                print("--------------------")
                match = re.match("arec.test.com.\s+\d+\s+IN\s+A\s+10.35.118.2", output[index+1])
                match1= re.match("arec.test.com.\s+\d+\s+IN\s+A\s+10.36.198.3", output[index+1]) 
                if match:
                    server1_found = True
                    
                if match1:
                    server2_found = True
                    
                    
        if server1_found or server2_found ==True:
            print("Success: Perform dig query")
            assert True
        else:
            print("Failed: Perform dig query")
            print(output)
            assert False
        
        
        
        
        
        
        
        