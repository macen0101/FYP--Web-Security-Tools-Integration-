import subprocess
import os
import json,sys
from multiprocessing import Process

class Whatweb:
    temp_json_path = f"{os.path.dirname(__file__)}/temp/temp_whatweb.json"
    def __init__(self, url ) -> None:
        self.url = str(url)
        
        whatweb_search_path_list=("whatweb", "/usr/bin/whatweb", "/usr/local/bin/whatweb",f"{os.path.dirname(__file__)}/../../FYP_ext_tools/WhatWeb/whatweb",f"{os.path.dirname(__file__)}/../../../FYP_ext_tools/WhatWeb/whatweb", f"{os.path.dirname(__file__)}/../../../../FYP_ext_tools/WhatWeb/whatweb", )
        
        for whatweb_path in whatweb_search_path_list:
            try:
                subprocess.Popen(
                        [whatweb_path],
                        bufsize = 10000,
                        stdout = subprocess.PIPE,
                    )
            except OSError:
                pass
            else:
                self.whatweb_path = whatweb_path
                break
        else:
            print("Whatweb program was not found.")
        
    
    def whatweb_scan(self, user_agnet:str="whatweb"): 
        Whatweb.clear_json()
        self.whatweb_raw_result_list = list()
        # cmd = f"{os.path.dirname(__file__)}/whatweb/whatweb_tools/whatweb -v --color=never {self.url} --user-agent {user_agnet} --log-json {Whatweb.temp_json_path} "
        cmd = f"{self.whatweb_path} -v --color=never {self.url} --user-agent '{user_agnet}' --log-json {Whatweb.temp_json_path} "
        result = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")
        result = result.stdout.readlines()
        for loop in result:
            self.whatweb_raw_result_list.append(loop)
            
        with open(Whatweb.temp_json_path) as user_file:
            parsed_json = json.load(user_file)
        return parsed_json 
    
    def clear_json():
        if os.path.exists(Whatweb.temp_json_path):
            os.remove(Whatweb.temp_json_path)
            return True
        return False
    
    def whatweb_goscan_and_filter(self,user_agnet:str="whatweb"):
        self.target_info_cms_name = ""
        self.target_info_cms_version = ""
        self.target_info_cms_wordlist = ""
        self.target_info_OS = ""
        self.target_web_server = ""

        all_result  = self.whatweb_scan(user_agnet=user_agnet)
        cms_wordlist_dict = Whatweb.cms_wordlist_dict()
    
        #if url have URL redir
        if len(all_result) == 1: 
            target_web_information = all_result[0]
        elif len(all_result) > 1:
            target_web_information = all_result[len(all_result)-1]
        elif len(all_result) == 0:
            return "Error"

        for plugin in target_web_information['plugins']:
            plugin_lower = plugin.lower()
            #detect CMS
            if plugin_lower in cms_wordlist_dict:
                ##cms name
                self.target_info_cms_name = plugin
                ##cms version
                try:
                    self.target_info_cms_version = target_web_information['plugins'][plugin].get('version')
                    if type(self.target_info_cms_version) == list:
                        self.target_info_cms_version = target_web_information['plugins'][plugin].get('version')[0]
                except:
                    self.target_info_cms_version = ""
                ##cms Wordlist
                self.target_info_cms_wordlist = cms_wordlist_dict[plugin_lower]

            #detect OS and webserver
            if plugin == 'HTTPServer':
                ##OS
                try:
                    self.target_info_OS = target_web_information['plugins'][plugin].get("os")
                    if type(self.target_info_OS) == list and len(self.target_info_OS) != 0:
                        self.target_info_OS = self.target_info_OS[0]
                except:
                    self.target_info_OS = ""
                ##web server
                try:
                    self.target_info_web_server = target_web_information['plugins'][plugin].get("string","")
                    if type(self.target_info_web_server) == list and len(self.target_info_web_server) != 0:
                        self.target_info_web_server  = self.target_info_web_server[0]
                except:
                    self.target_info_web_server  = ""
        return True

    def cms_wordlist_dict():
        cms_wordlist_dict = dict()
        try:
            directory = f"{os.path.dirname(__file__)}/../Wordlists/CMS"
            for type in os.listdir(directory):
                f = os.path.join(directory, type)
                if os.path.isfile(f):
                    names = type.rsplit('.', 1)[0].lower()
                    cms_wordlist_dict[names]=f"{directory}/{names}.txt"
        except FileNotFoundError:
            print("config file not found")
        return cms_wordlist_dict
    
    def choose_wordlist(self,user_agnet:str="whatweb"):
        scan_result = self.whatweb_goscan_and_filter(user_agnet=user_agnet)
        if scan_result == True:
            cms_name = self.target_info_cms_name
            cms_version = self.target_info_cms_version
            cms_wordlist = self.target_info_cms_wordlist
            web_server = self.target_info_web_server
            system_os = self.target_info_OS
            if cms_name == "":
                cms_name = "unkwon"
            if cms_version == "":
                cms_version = "unkwon"
            if cms_wordlist == "":
                cms_wordlist = f"{os.path.dirname(__file__)}/../Wordlists/common.txt"
            cms_wordlist_dict = {"target_url":self.url,"web_server":web_server,"OS":system_os,"CMS_name":cms_name,"CMS_version":cms_version ,"wordlist":cms_wordlist} 
            return cms_wordlist_dict, self.whatweb_raw_result_list
        else:
            return False, False

if __name__=="__main__":
    # url = "http://192.168.1.50/"
    # url = "http://owasp.local/wordpress/"
    url = "http://owasp.local/joomla/"

    test = Whatweb(url)
    data = test.choose_wordlist()
    print(data)