import subprocess
import os
import re

class Nikto:
    def __init__(self, url,user_agent="Nikto"):
        self.url = list(url) #www.google.com:80
        self.tool = "nikto"
        self.host_arg = "-h"
        self.user_agent_arg = "-useragent"
        self.user_agent = user_agent
        self.cmd = list()

    def tool_exists(self):
        try:
            devnull = open(os.devnull)
            subprocess.Popen([self.tool], stdout=devnull, stderr=devnull).communicate()
        except OSError as error:
            if error.errno == os.error.ENOENT:
                return False
            else:
                return True
            
    def handler(self):
        for x in self.url:
            return x['url']

    def nikto_scan(self):
        self.temp_raw_result_array = []
        self.temp_filtered_result_array = []
        self.nikto_raw_result = list()
        
        # if self.tool_exists() == True:
        # for url_item in self.url_list:
        #     # for key in url_item:
        #         self.url = url_item['target_address']
        self.cmd = [self.tool, self.host_arg, self.handler(), self.user_agent_arg, self.user_agent]
        result = self.execute()
            
        for line in result:
            self.nikto_raw_result.append(line)
            found = line.find('+ OSVDB-')
            if found != -1:
                self.temp_raw_result_array.append(line)
                
        for final in self.temp_raw_result_array:
            found_final = final.find("/?")
            if found_final != -1:
                # print(final)
                self.temp_filtered_result_array.append(final)
                
        return {"raw":self.temp_raw_result_array,"filtered":self.temp_filtered_result_array}, self.nikto_raw_result

    def execute(self):
        result = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")
        result = result.stdout.readlines()

        return result

if __name__=="__main__":
    nikto = Nikto(url=[{'url':"owasp.local"}],user_agent="testing")

    print(nikto.nikto_scan())
