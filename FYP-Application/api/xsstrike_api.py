import subprocess
import os
import re


XSSTRIKE_PATH = "/Users/xxxx/Desktop/FYP_ext_tools/XSStrike/xsstrike.py"

class XSStrike:
    
    def __init__(self, target, headers=None, skip_dom:bool=False,fuzzer_mode:bool = False, time_out=None, request_method:str="get", xsstrike_filter_arg=False):
        self.target = target
        self.url_arg = "-u"
        self.headers_arg = "--headers"
        self.fuzzer_arg = "--fuzzer"
        self.skip_dom_arg = "--skip-dom"
        self.skip_arg = "--skip"
        self.request_method = request_method
        self.time_out = time_out
        self.headers = headers
        self.xsstrike_filter_arg = xsstrike_filter_arg
        self.data_arg = "--data"
        self.skip_dom = skip_dom
        self.fuzzer_mode = fuzzer_mode

    def xsstrike_scan(self):
        if self.request_method == "get":
            cmd = ["python3", XSSTRIKE_PATH, self.url_arg, self.target, self.skip_arg]
            #python3 xsstrike.py -u http://test.com --skip

            if self.skip_dom == True:
                #python3 xsstrike.py -u http://test.com --skip --skip-dom
                cmd.append(self.skip_dom_arg)

            if self.fuzzer_mode == True:
                #python3 xsstrike.py -u http://test.com --skip --skip-dom --fuzzer
                cmd.append(self.fuzzer_arg)
                
            if self.headers == None:
                cmd = cmd
            elif self.headers != None:
                #python3 xsstrike.py -u http://test.com --skip --headers "Cookie"
                #python3 xsstrike.py -u http://test.com --skip --skip-dom --fuzzer --headers "Cookie"
                #python3 xsstrike.py -u http://test.com --skip --skip-dom --headers "Cookie"

                cmd.extend([self.headers_arg, self.headers])
            
            result = self.execute_command(cmd)
            # print("----------result---------------")
            # print(result)
            # result = [" Checking for DOM vulnerabilities ",
                        # " Potentially vulnerable objects found ",
                        # "------------------------------------------------------------",
                        # "3   $('#backLink').attr('href', (new URLSearchParams(window.*location.search*)).get('returnPath'));",
                        # "------------------------------------------------------------"]
            
            # filtering
            if self.xsstrike_filter_arg == True:
                final_result = {}
                # fuzzer filtering
                if self.fuzzer_mode == True:
                    final_result = self.fuzzer_filter(result=result)
                    return result, final_result
                
                # DOM filtering
                if self.skip_dom == False:
                    filtered_DOM_result = []
                    a = False
                    b = False
                    c = False
                    for line in result:
                        if line.find("Checking for DOM vulnerabilities") != -1:
                            a = True
                            continue
                        if line.find("Potentially vulnerable objects found") != -1:
                            b = True
                            continue
                        if line.find("------------------------------------------------------------") != -1:
                            c = True
                            continue
                        if a == True and b == True and c == True:
                            if line.find(" Payload: ") != -1 or line.find(" Efficiency: ") != -1 or line.find(" Confidence:") != -1:
                                # continue
                                # break
                            # if line.find():
                                filtered_DOM_result.append(line)

                    if b == True:
                        final_result["DOM"] = True
                        #message box
                    else:
                        final_result["DOM"] = "Maybe not DOM XSS Vulnerability"
                    pass
                    
                # Payload filtering
                filtered_Payload_result = []
                payload_keyword = r'Payload:\s(.*)\n'
                for line in result:
                    if re.match(payload_keyword, line):
                        filtered_Payload_result.append(line)
                    else:
                        continue
                if len(filtered_Payload_result) != 0:
                    final_result["Payload"] = filtered_Payload_result
                else:
                    final_result["Payload"] = "May not provide payload"

                print(final_result)
                return result,final_result
            
            elif self.xsstrike_filter_arg == False:
                    return result, None #raw , filted     

    def execute_command(self,cmd):
        run = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")
        print(cmd)
        run = run.stdout.readlines()
        return run

    def fuzzer_filter(self,result):
        temp_array = list()
        for line in result:
            if line.find("[passed]") != -1:
                filted = line.replace("[passed]","")
                filted = filted.strip()
                temp_array.append(filted)

        print(temp_array)
        return temp_array
            
if __name__ == "__main__":
    xsstrike = XSStrike(target="", headers="Cookie: ; security=low", xsstrike_filter_arg=True, skip_dom=False)
    result = xsstrike.xsstrike_scan()
    print(result)
