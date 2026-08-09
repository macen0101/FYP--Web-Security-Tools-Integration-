import urllib3
import re,socket,requests
import nmap3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class Nmap_scan:
    http_servers_lists = ["Nginx", "Apache", "Cloudflare", "LiteSpeed", "IIS", "Tengine", "Cowboy","SimpleHTTPServer","HTTP"]

    def __init__(self, ip, start_port:int=None, end_port:int=None) -> None:
        # super().__init__(self.url)
        
        checkInputType = re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", ip)
        # using a IP address RegEx to check the input data either ip or url, if it is a URL, the program will swith it to ip and return it
        if not checkInputType: # If input is IP
            self.__ip = socket.gethostbyname(ip)
        elif checkInputType:
            self.__ip = ip

        self.__start_port = start_port
        self.__end_port = end_port

        # This function purpose is switching target's Ip address and URL for different scanning processes
    
    def nmap_OS_dect(self):
        nmap = nmap3.Nmap()
        self.__nmap_results = nmap.nmap_version_detection(self.__ip)
        # for port in self.__nmap_results[self.__ip]['ports']:
        #     temp_namp_OS = port['service'].get('ostype',"")
        #     temp_nmap_port_status = 0
        #     if port.get('state')=='open':
        #         temp_nmap_port_status = 1
        #     # print(database_id,self.__ip,port['portid'],temp_nmap_port_status,port['service'].get('name',""),port['service'].get('product',""),port['service'].get('version',""),temp_namp_OS)
        #     database.DB_connect.insert_tools_receivedData(database_id,
        #     {"tools":'nmap',
        #     "scanning_type":'OS',
        #     "ip":f'{self.__ip}',
        #     "port":f'{port["portid"]}',
        #     "port_status":f'{temp_nmap_port_status}',
        #     "service":f'{port["service"].get("product","")}',
        #     "OS":f'{temp_namp_OS}'
        #     }
        #     )
        return self.__nmap_results

    def get_running_web_server_info(self,target_server_address:str):
        
        user_agent = {'User-agent': 'Mozilla/5.0'}
        self.web_server_list = list()
        temp_web_server_list = list()
        self.all_result_raw = self.nmap_OS_dect()
        
        for port in self.all_result_raw[self.__ip]['ports']:
            for name in Nmap_scan.http_servers_lists:
                temp_product_name = port['service'].get('product','').lower()
                if temp_product_name.find(name.lower()) != -1 and port['state']=='open':
                    temp_web_server_info = { 
                        'ip_address':self.__ip,
                        'portid':port['portid'], 
                        'product':port['service']['product'],
                        'version':port['service'].get('version',"")
                    }
                    temp_web_server_list.append(temp_web_server_info)

                    break

        for port in temp_web_server_list:
            request_status = False
            temp_protocol="http://" 
            temp_target_address = f"http://{target_server_address}:{port['portid']}"
            try:
                r = requests.get(temp_target_address , headers= user_agent, verify=False, timeout=2)
                request_status = True
            except :
                pass
 
            if not r:
                try:
                    temp_target_address = f"https://{target_server_address}:{port['portid']}"
                    r = requests.get(temp_target_address , headers= user_agent, verify=False , timeout=2)
                    temp_protocol="https://" 
                    request_status = True
                except :
                    break
            # print(f"{temp_target_address} {r.status_code}")  
            if request_status == True:
                # url=f"{temp_protocol}{target_server_address}:{port['portid']}
                data = {
                    'url':f"{temp_protocol}{target_server_address}:{port['portid']}", 
                    'portid':port['portid'],
                    'product':port['product'],
                    'version':port['version']
                    }                
                self.web_server_list.append(data)         
        
        return self.web_server_list, self.all_result_raw
    
if __name__ == "__main__":
    address = "owasp.local"
    # address = "xyz.chan2001.com"

    x = Nmap_scan(address)
    # print( x.nmap_OS_dect() )
    print( x.get_running_web_server_info(target_server_address=address) )