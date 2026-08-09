import subprocess
import re
import sys
import socket
import time
import json
import nmap3
import requests
import urllib3
import os
import threading
import datetime

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#import python file code
import tinydb_database as database
# import api.screenshot as website_screenshot
from api.nmap_api import Nmap_scan
from api.gobuster_api import Gobuster
from api.whatweb_api import Whatweb
from api.nikto_api import Nikto



# self.tools_config = {
        # 'Nmap':{"open":0,"scan_mode":""} ,
        # 'Gobuster':{"open":0,"mode":"dir"},
        # 'WhatWeb':{"open":0},
        # 'Nikto':{"open":0},
        # 'XSStrike':{"open":0},
        # 'SQLmap':{"open":0}
        # }

class Scan:
    def __init__(self, url:str, tools_config:dict, user_agent:str = "FYP_tools", custom_wordlist_path:str = f"{os.path.dirname(__file__)}/Wordlists/common.txt"):
        self.url = str(url)
        self.tools_config = dict(tools_config)
        self.user_agent = user_agent
        self.custom_wordlist_path = custom_wordlist_path
        self.user_wordlist:str = None
        if self.user_agent == "random_normal_browser":
            self.user_agent = self.random_user_agent()

    def random_user_agent(self): #for random select user agent from user agents wordlist
        import random
        user_agent_wordlist = list()
        try:
            with open(f"{os.path.dirname(__file__)}/Wordlists/user_agents_wordlist.txt") as f:
                for line in f:
                    user_agent_wordlist.append(line.rstrip('\n'))
            return random.choice(user_agent_wordlist)
        except FileNotFoundError:
            print("user_agent_wordlist File NOT Found")
            return "FYP Tools"

    def url_filter(self): #change doamin name to ip address and slipt URL and directory
        self.target_server_address_url= re.findall(r"^(?:https?:\/\/)?(?:[^@\/\n]+@)?(?:www\.)?([^:\/\n]+)", self.url)
        self.target_server_address_ip = socket.gethostbyname(self.target_server_address_url[0])
        if self.url.find("http://") != -1 or self.url.find("https://") !=1:
            self.target_server_url_path = re.findall(r"^https?:\/\/[A-Za-z0-9:.]*([\/]{1}.*\/?)$", self.url)
        else:    
            self.target_server_url_path = re.findall(r"[A-Za-z0-9:.]*([\/]{1}.*\/?)$", self.url)
        return self.target_server_address_url, self.target_server_url_path
        # self.types = "dir"
        # self.wordlist = f"{os.getcwd()}/Wordlists/common.txt"

    def main(self): #create new scan event
        self.url_filter()
        self.database_id = database.DB_connect.insert_new_event(self.url, self.target_server_address_ip, self.tools_config,self.user_agent)
            
        pass

    def get_current_database_id(self): #get current scanning event database id
        return self.database_id
    
    def tools_nmap(self): #call nmap tools
        ## Nmap
        if self.tools_config['Nmap'].get("open",0) == 1: #if user enable Nmap tools
            nmap = Nmap_scan(self.target_server_address_ip)
            self.nmap_web_server_dict_list,self.nmap_raw_result = nmap.get_running_web_server_info(self.target_server_address_url[0])
            #raw
            for item in self.nmap_web_server_dict_list:
                data =  {"tools": "nmap", "target_address": item['url'],"portid":item['portid'], "scanning_type": "OS","Product":item['product'],"Version":item['version']}
                database.DB_connect.insert_tools_receivedData(self.database_id,data)
            return self.nmap_raw_result
        elif self.tools_config['Nmap'].get("open") == 0: #if user disable Nmap tools
            # self.nmap_web_server_dict_list = [self.url.replace(self.target_server_url_path[0],"")]
            try:
                temp_url = self.url.replace(self.target_server_url_path[0],"")
            except:
                temp_url = self.url
                
            self.nmap_web_server_dict_list = [{'url':temp_url}]
            #raw
            print("message: nmap disable")
            return self.nmap_web_server_dict_list
        else:
            return False
        
    # get web server list    
    def choose_nmap_web_server_dict_list(self,user_choose:list=None): 
        self.nmap_web_server_dict_list = user_choose
    
    # call tool whatweb to scan web technology    
    def tools_whatweb(self):
        ## Whatweb
        self.whatweb_results_list=list()
        if self.tools_config['WhatWeb'].get("open") == 1:
            for url_item in self.nmap_web_server_dict_list:
                # Call WhatWeb  API
                try:
                    whatweb = Whatweb(url_item['url']+self.target_server_url_path[0])
                except:
                    whatweb = Whatweb(url_item['url'])
                temp_whatweb_result,whatweb_raw_result = whatweb.choose_wordlist(user_agnet=self.user_agent) 
                self.whatweb_results_list.append(temp_whatweb_result)
                for line in self.whatweb_results_list:
                    if line != "Error":
                        data = {"tools":'WhatWeb'}|line
                        database.DB_connect.insert_tools_receivedData(self.database_id,data)

        elif self.tools_config['WhatWeb'].get("open") == 0:# if tool disable
            self.whatweb_results_list.append({"target_url": self.url,"CMS_name":"non gobuster select wordlist", "wordlist":self.custom_wordlist_path})
            print("message: whatweb disable")
            return False
        else:
            print("tools_whatweb miss enable option")
            return False
        
        return whatweb_raw_result
    
    def choose_gobuster_dir_wordlist(self,user_choose_wordlist:str = None):
        print(user_choose_wordlist)
        self.user_wordlist = user_choose_wordlist

    def tools_gobuster(self):
        # ## Gobuster
        self.gobuster_result_dict = dict()
        if self.tools_config['Gobuster'].get("open") == 1:
            # Call Gobuster API
            gobuster = Gobuster(user_agent=self.user_agent)
            # Use dir mode
            if self.tools_config['Gobuster'].get("mode") == "dir":
                for item in self.whatweb_results_list:
                    if self.user_wordlist != None: #user wordlist
                        gobuster_dir_results,gobuster_dir_raw_results = gobuster.gobuster_scan(target_information=item,mode="dir",user_wordlist=self.user_wordlist)
                    else: #default wordlist
                        gobuster_dir_results,gobuster_dir_raw_results = gobuster.gobuster_scan(target_information=item,mode="dir")
                    self.gobuster_result_dict[item['target_url']] = gobuster_dir_results #gobuster result
                    for result in gobuster_dir_results:
                        data = {"tools":'Gobuster',"mode":"dir"} | result
                        database.DB_connect.insert_tools_receivedData(self.database_id,data)
                print(self.gobuster_result_dict)
                return self.gobuster_result_dict, gobuster_dir_raw_results
            # Use subdomain mode
            elif self.tools_config['Gobuster'].get("mode") == "subdomain":
                if self.user_wordlist != None:
                    gobuster_subdomain_result,gobuster_subdomain_raw_result = gobuster.dns_scan(url=self.url,wordlist=self.user_wordlist)
                else:
                    gobuster_subdomain_result,gobuster_subdomain_raw_result = gobuster.dns_scan(url=self.url)
                #miss "gobuster_subdomain_result" formating
                for subdomain in gobuster_subdomain_result:
                        if self.user_wordlist != None:
                            data = {"tools":'Gobuster',"mode":"subdomain","subdomain":subdomain,"used_wordlist":self.user_wordlist}
                        else:
                            data = {"tools":'Gobuster',"mode":"subdomain","subdomain":subdomain,"used_wordlist":gobuster.get_used_wordlist()}
                        database.DB_connect.insert_tools_receivedData(self.database_id,data)
                return gobuster_subdomain_result,gobuster_subdomain_raw_result
                pass
            # Use vhost mode
            elif self.tools_config['Gobuster'].get("mode") == "vhost":
                if self.user_wordlist != None:
                    gobuster_vhost_result,gobuster_vhost_raw_result = gobuster.vhost_scan(url=self.url,wordlist=self.user_wordlist)
                else:
                    gobuster_vhost_result,gobuster_vhost_raw_result = gobuster.vhost_scan(url=self.url)
                for key in gobuster_vhost_result:
                        for vhost in gobuster_vhost_result[key]:
                            if self.user_wordlist != None:
                                data = {"tools":'Gobuster',"mode":"vhost","vhost":vhost,"http_status":key,"used_wordlist":self.user_wordlist}
                            else:
                                data = {"tools":'Gobuster',"mode":"vhost","vhost":vhost,"http_status":key,"used_wordlist":gobuster.get_used_wordlist()}
                            database.DB_connect.insert_tools_receivedData(self.database_id,data)
                return gobuster_vhost_result,gobuster_vhost_raw_result
                pass
            else:
                pass
        elif self.tools_config['Gobuster'].get("open") == 0:
            return "gobuster disable", None
        else:
            print("tools_gobuster miss enable option")
            return False, False
    
    # Call tool Nikto to find web server miss configuration     
    def tools_nikto(self):
        # ## Nikto
        
        if self.tools_config['Nikto'].get("open",0) == 1:
            print("message: Nikto start")
            # print("testing tools 133:",self.nmap_web_server_dict_list)
            # Call Nikto API
            nikto = Nikto(url = self.nmap_web_server_dict_list,user_agent=self.user_agent)
            results,nikto_raw_result = nikto.nikto_scan()
            for type in results:
                for result in results[type]:
                    data = {"tools":'Nikto', "type":type, "result":result}
                    database.DB_connect.insert_tools_receivedData(self.database_id,data)
            return nikto_raw_result
        else:
            return False

    def get_current_DB_id(self):
        return self.database_id

if __name__=="__main__":
    target_url = "owasp.local/wordpress"
    web_server_list = list()
    tools_config = {
        'Nmap':{"open":1} ,
        'WhatWeb':{"open":1},
        'Gobuster':{"open":1},
        'Nikto':{"open":0},
        'XSStrike':{"open":0},
        'SQLmap':{"open":0}
        }
    print(tools_config,"\n")
    scan = Scan(url=target_url, tools_config=tools_config)
    scan.main()
    scan.tools_nmap()
    scan.tools_whatweb()
    x = scan.tools_gobuster()
    print("\n (testing tools.py line 155)gobuster result \n",x)
   