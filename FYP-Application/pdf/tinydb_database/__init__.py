from tinydb import TinyDB ,Query,table
import os
import datetime
class DB_connect:
    db_file = TinyDB(f'{os.path.dirname(__file__)}/database.json')
    myDBQuery= Query()

    def get_current_time():
        now = datetime.datetime.now()
        return now.strftime("%Y-%m-%d %X")

    def insert_new_event(domain:str="",ip:str="",tools_config_dict:dict={},user_agent:str=""): 
        id = DB_connect.db_file.insert({
        'date_time': DB_connect.get_current_time() ,
        'target_server_domain': domain,
        'target_server_ip': ip,
        'tools_user_agent':user_agent,
        'tools_config':
          tools_config_dict,
        'tools_receivedData':[
            
        ],
        })
        return id

    def insert_tools_receivedData(id,receivedData): 
        try:
            from tinydb.operations import add
            DB_connect.db_file.update(add('tools_receivedData',[receivedData]), doc_ids= [id])
            return True
        except:
            return False
    
    def update_tools_config(id,data):
        
        pass
    
    def get_one_tool_result(id,tool_name):
        try:
            temp_result_list = list()
            temp_all_record = DB_connect.db_file.get(doc_id=id) #all_record['tools'] == tool_name, 
            temp_all_tools_receivedData = temp_all_record['tools_receivedData']#.get(tool_name)
            for record in temp_all_tools_receivedData:
                if record.get("tools").lower() == tool_name.lower():
                    temp_result_list.append(record)
            return temp_result_list
        except:
            print("database internal error")
            return []
    
    def get_tool_enable_status(id,tool_name):
        temp_all_record = DB_connect.db_file.get(doc_id=id) 
        return temp_all_record['tools_config'][tool_name].get("open",None)
    
    ########################
    #whatweb_screenshot_url#
    ########################
    def get_url_list_for_website_screenshot(id):
        url_list = list()
        db_all_record = DB_connect.db_file.get(doc_id=id)
        for line in db_all_record.get("tools_receivedData"):
            if line.get("tools",None) == "gobuster" and line["url"]:
                url_list.append(line["url"])
        return url_list

    def insert_gobuster_website_screenshot_path(id,screenshot_path_dict_list):
        db_all_record = DB_connect.db_file.get(doc_id=id)
        updated_list = list()
        # website_screenshoot_list.append({"url":url,"status":True,"png_path":new_path})?
        # for line in screenshot_path_dict_list:
        for db_line in db_all_record.get("tools_receivedData"):
            for line in screenshot_path_dict_list:
                if db_line.get("tools",None) == "gobuster" and db_line.get("url",None) == line["url"]:
                    db_line["png_path"] = line['png_path']           
            updated_list.append(db_line)
        id  = DB_connect.db_file.update({'tools_receivedData':updated_list}, doc_ids=[id])
        print(id)
        return id
        # for line in screenshot_path_dict_list:
    def delete_record_by_id(id):
        status = DB_connect.db_file.remove(doc_ids=[id])
        return status
    
    def get_all_record_id_datetime_address():
        db_id_list = list()
        db_all_record = DB_connect.db_file.all()
        if db_all_record:
            for line in db_all_record:
                db_id_list.append({
                             'id':line.doc_id,
                             'datetime':line.get('date_time',''),
                             'target_address':line.get('target_server_domain',''),
                             'target_server_ip':line.get('target_server_ip','')
                                                        })
        return db_id_list

    def get_reocrd(id):
        try:
            record = DB_connect.db_file.get(doc_id=id)
            return record
        except:
            return {}
        
    def get_record_for_result_page(id):
        try:
            record = DB_connect.db_file.get(doc_id=id)
        except:
            return {}
        
        receivedData_exist_tools_list =list()
        for receivedData_line in record.get("tools_receivedData",{}):
            if receivedData_line.get("tools","").lower() not in receivedData_exist_tools_list:
                receivedData_exist_tools_list.append(receivedData_line.get("tools","").lower())
        
        all_record = record
        target_url = record.get("target_server_domain","")
        

        result_info = {"all_record":all_record,
                       "target_url":target_url,
                       "date_time":record.get("date_time",""),
                       "user_agent":record.get("tools_user_agent",""),
                       "result_exist_tools_list":receivedData_exist_tools_list,
                       "tools_config":record.get("tools_config","")
                        }
        
        return result_info

        
    
if __name__ == "__main__": #For test Use
    results = DB_connect.get_one_tool_result(id=26, tool_name="xsstrike")
    print(results)
