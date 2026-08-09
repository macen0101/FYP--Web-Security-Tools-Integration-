import subprocess
import os
import re
import sys
import socket
import requests
from multiprocessing import Process

try:
    from screenshot_api import ScreenShot
except ImportError:
    from .screenshot_api import ScreenShot
    
class Gobuster:
    def __init__(self,user_agent="gobuster", gobuster_search_path=("gobuster", "/usr/bin/gobuster", "/usr/local/bin/gobuster", ),) -> None:
        self.gobuster_path:str = ""
        self.scan_result:dict = {}
        self.gobuster_version:int = 0
        self.gobuster_subversion:int = 0
        self.gobuster_last_output:str = ""
        self.gobuster_exisit:bool = False
        self.status_code = [200, 301, 302, 403]

        # result 
        self.result_dir_scan_status_dict= {}
        self.result_dns_scan=list()
        self.result_vhost_http_status_dict = {}

        version_regex:re = re.compile(r"[0-9]*\.[0-9]*[^ ]*\-dev")
        
        for gobuster_path in gobuster_search_path:
            try:
                if (
                    sys.platform.startswith("linux") or 
                    sys.platform.startswith("freebsd") or 
                    sys.platform.startswith("darwin") or 
                    sys.platform.startswith("win32")
                ):
                    run_gobuster_version = subprocess.Popen(
                        [gobuster_path, "version"],
                        bufsize = 10000,
                        stdout = subprocess.PIPE,
                        close_fds = True,
                    )
                else:
                    run_gobuster_version = subprocess.Popen(
                        [gobuster_path, "version"],
                        bufsize = 10000,
                        stdout = subprocess.PIPE,
                    )
            except OSError:
                pass
            else:
                self.gobuster_path = gobuster_path
                break
        else:
            print("Gobuster program was not found.")

        # self.gobuster_last_output = bytes.decode(run_gobuster_version.communicate()[0])

####################################
#       Gobuster's arguments       #
####################################
        self.url_argument:str="-u"
        self.dns_argument:str="-d"
        self.wordlist_argument:str="-w"
        self.extension_argument:str="-x"
        self.vhost_scan_argument:str="-v"
        self.user_agent_argument:str="-a"
        self.append_domain:str="--append-domain"
####################################
#       files elements             #
####################################
        self.files_types:list = ["js", "php"]
        self.type:str = ""
####################################
#       User agent             #
####################################
        self.user_agent = user_agent

####################################
#       Gobuster's functions       #
####################################
    def get_used_wordlist(self):
        return self.used_wordlist
    def get_gobuster_path(self):
        pass

    def dir_scan(self, url:str, types:str="dir", wordlist:str=f"{os.path.dirname(__file__)}/gobuster/default_wordlist_dir_php.txt") -> str:
    # def dir_scan(self, url:str, types:str="dir", wordlist:str="/Users/daniel/Desktop/SecLists/Discovery/Web-Content/apache.txt") -> str:
        self.used_wordlist = wordlist
        self.target_url = url
        for file_type in self.files_types:
            self.type += file_type + ","

        cmd:str = f"{self.gobuster_path} {types} {self.url_argument} {url} {self.wordlist_argument} '{wordlist}' {self.user_agent_argument} '{self.user_agent}' {self.extension_argument} {self.type} "
        dir_result = self.execute_command(cmd)
        # print("hihi",type(dir_result))
        for line in dir_result:
            found = line.find('\x1b[2K/')
            if found != -1:
                line = line.replace('\x1b[2K',"")
                line = line.split()
                temp_url=line[0]
                temp_status=line[2].replace(")","")
                
                if temp_status not in self.result_dir_scan_status_dict:
                    self.result_dir_scan_status_dict[f"{temp_status}"]={"url":[], "re_url":[]} 

                try:
                    temp_url_redirection=line[6].replace("]","")
                    self.result_dir_scan_status_dict[f"{temp_status}"]['re_url'].append({"orig_url":temp_url,"re_dir_url":temp_url_redirection})
                except:
                    self.result_dir_scan_status_dict[f"{temp_status}"]['url'].append(temp_url)

        return self.result_dir_scan_status_dict,dir_result

    def dns_scan(self, url:str, types:str="dns", wordlist:str=f"{os.path.dirname(__file__)}/gobuster/default_wordlist_subdomains.txt") -> str:
        self.used_wordlist = wordlist
        if url.find("http://") or url.find("https://"):
            url = url.replace("http://","")
            url = url.replace("https://","")
        cmd:str = f"{self.gobuster_path} {types} {self.dns_argument} {url} {self.wordlist_argument} {wordlist}"
        dns_result = self.execute_command(cmd)
        self.raw_result_dns_scan = list()
        for line in dns_result:
            self.raw_result_dns_scan.append(line)
            found = line.find('\x1b[2KFound:')
            if found != -1:
                line = line.replace('\x1b[2KFound:', "")
                line = line.split()
                line = line[0]
                self.result_dns_scan.append(line)
                
        return self.result_dns_scan, self.raw_result_dns_scan

    def vhost_scan(self, url:str, types:str="vhost", wordlist:str=f"{os.path.dirname(__file__)}/gobuster/default_wordlist_vhost.txt") -> str:
        self.used_wordlist = wordlist
        cmd:str = f"{self.gobuster_path} {types} {self.vhost_scan_argument} {self.url_argument} {url} {self.wordlist_argument} {wordlist} {self.user_agent_argument} '{self.user_agent}' {self.append_domain}" 
        vhost_result = self.execute_command(cmd)
        temp_array = []
        self.raw_result_vhost_http_status_dict = list()
        for line in vhost_result:
            self.raw_result_vhost_http_status_dict.append(line)
            found = line.find('\x1b[2KFound:')
            if found != -1:
                line = line.replace('\x1b[2KFound:', "")
                line = line.split()
                temp_array.append(line)

        for record in temp_array:
            if record[2] not in self.result_vhost_http_status_dict:
                self.result_vhost_http_status_dict[f"{record[2]}"]=[record[0]]
            else:
                self.result_vhost_http_status_dict[f"{record[2]}"].append(record[0])
#result_vhost_http_status_dict = [{400:['www','www2']}]
        return self.result_vhost_http_status_dict,self.raw_result_vhost_http_status_dict

    def execute_command(self, cmd) -> str:
        run = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")
        run = run.stdout.readlines()
        return run

    def gobuster_filter(self, file_type:str="php"): 
        self.found_url_list= list()
        temp_url_dict=dict()
        # temp_filter_wordlists=list()
        # #open wordlists
        # with open(f'{os.getcwd()}/Wordlists/filter_wordlists.txt', "r") as f:
        #     f_contents = f.readlines()
        #     for content in f_contents:
        #         content=content.replace("\n", "")
        #         temp_filter_wordlists.append(content)
        #end open wordlists

        # for url in self.result_dir_scan_status_dict["200"]["url"]:
            # found = url.find(url)
            # if found != -1:
            # temp_url_dict[url]= "200"
        
        # regex_array = [r".*admin.*", r".*login.*", r".*logon.*", r".*error.*", r".*log.*", r".*debug.*", r".*upload.*", r".*edit.*", r".*user.*", r".*install.*", r".*index.*"]
        # path = f"{os.path.dirname(__file__)}/gobuster/gobuster_default_filter.txt"
        path = f"{os.path.dirname(__file__)}/gobuster/gobuster_temp_URL_filter.txt"
        regex_array = []
        try:
            with open(path) as file:
                lines = file.readlines()
                for line in lines:
                    line = line.rstrip("\n")
                    regex_array.append(line)
        except FileNotFoundError:
            print("gobuster_filter Not Found")
            return False

        #########################
        #check status 200 url
        if self.result_dir_scan_status_dict.get("200",None) != None:
            for url in self.result_dir_scan_status_dict["200"].get("url",[]):
                for regex in regex_array:
                    regex_result = re.findall(regex, url, re.I)
                    if regex_result and url.find(".php") != -1 or url.find(".html") != -1 or url.find(".htm") != -1:
                        print(url)
                        self.found_url_list.append(url)
                        break
        
        #check status 301 url
        if self.result_dir_scan_status_dict.get("301",None) != None:
            for url_item in self.result_dir_scan_status_dict["301"].get("re_url",[]):
                try:
                    url = url_item.get('re_dir_url',None)
                    orig_target_address = self.target_url.split("/")[2]
                    orig_target_address = orig_target_address.split(":")[0]
                    if url != None and url.find(orig_target_address) != -1 :
                        user_agent = {'User-agent': self.user_agent}
                        request = requests.get(url_item.get('re_dir_url'), headers= user_agent)
                        temp_http_status = request.status_code
                    else:
                        continue
                except:
                    continue
                if temp_http_status == 200:
                    print(url_item['orig_url'])
                    self.found_url_list.append(url_item['orig_url'])

        return self.found_url_list
    


    def go_check_redir_host(self):
        self.checked_redir_url = {'non_redir_url':[],'internal_redir_url':[],'outside_redir_url':[]}
        temp_reurl_list = list()
        for status_code in self.result_dir_scan_status_dict:
            for url in self.result_dir_scan_status_dict[status_code]["re_url"]:
                url = f"{self.target_url}{url['orig_url']}"
                temp_reurl_list.append(url)
        # print(temp_reurl_list)

        for url in temp_reurl_list:
            orig_doamin = re.findall(r"^(?:https?:\/\/)?(?:[^@\/\n]+@)?(?:www\.)?([^:\/\n]+)",url)
            orig_ip_address = socket.gethostbyname(orig_doamin[0])
            header = {'User-agent':self.user_agent}
            response = requests.get(url, headers = header)
            if response.history:   
                # for resp in response.history:  
                #     print(resp.status_code, resp.url)
                # print(response.status_code, response.url) #Final destination:
                response_doamin = re.findall(r"^(?:https?:\/\/)?(?:[^@\/\n]+@)?(?:www\.)?([^:\/\n]+)",response.url)
                response_ip_address = socket.gethostbyname(response_doamin[0]) 
            else:
                response_ip_address = None

            if orig_ip_address == response_ip_address:
                self.checked_redir_url['internal_redir_url'].append(url)
            elif orig_ip_address != response_ip_address:
                self.checked_redir_url['outside_redir_url'].append(url)
            elif response_ip_address == None:
                self.checked_redir_url['non_redir_url'].append(url)

        print(self.checked_redir_url)
        return self.checked_redir_url


    def gobuster_scan(self,target_information:dict,mode:str = "dir",user_wordlist:str=None):
        if mode == "dir":
            self.to_scan_all_result = list()
            self.filtered_url_list = list()
            if user_wordlist != None:
                gobuster_dir_scan_result,gobuster_dir_raw_result = self.dir_scan(url=target_information["target_url"], wordlist = user_wordlist) 
                print(user_wordlist)
            else:
                gobuster_dir_scan_result,gobuster_dir_raw_result = self.dir_scan(url=target_information["target_url"], wordlist = target_information["wordlist"])
                print(target_information["wordlist"]) 
            if len(gobuster_dir_scan_result) != 0: #if gobuster have result return
                risk_urls = self.gobuster_filter()
                for url_path in risk_urls:
                    self.filtered_url_list.append(target_information["target_url"]+url_path)

                if len(self.filtered_url_list) != 0 :
                    tools_SC = ScreenShot(self.filtered_url_list)
                    screenshot_results = tools_SC.main()
                    for result in screenshot_results: #to screenshot
                        temp_screenshot_status = result.get("status",False)
                        if temp_screenshot_status == True:
                            line = {"url":result['url'], "png_path":result['png_path'],"used_wordlist":target_information["wordlist"]}
                        elif temp_screenshot_status == False:
                            line = {"url":result['url'], "png_path":False,"used_wordlist":target_information["wordlist"]}
                        self.to_scan_all_result.append(line)
                    return self.to_scan_all_result,gobuster_dir_raw_result
                else:
                    print("gobuster NOT result")
                    return False
        else:
            return False
     
        #             database.DB_connect.insert_tools_receivedData(database_id,{"tools":'gobuster',"scan_type":'dir scan',"scan_wordlist":f'{whatweb_scan_list_dict[target_url]["wordlist"]}',"url":f'{target_url}{url_path}',"CMS_name":f'{whatweb_scan_list_dict[target_url]["CMS_name"]}',"png_path":''  } )

#     #take screenshot
# to_screenshot_list = database.DB_connect.get_url_list_for_website_screenshot(database_id) #get url list
# screenshoted_path_dict = website_screenshot.main(to_screenshot_list) #call funct
# database.DB_connect.insert_gobuster_website_screenshot_path(database_id,screenshoted_path_dict) #updata database

if __name__=="__main__":
    x = 1
    x = Gobuster()
    info,raw = x.vhost_scan(url="https://example.com")
    print(info)
