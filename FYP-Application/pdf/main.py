import pdfkit as pdf
import time
from tinydb_database import DB_connect
from datetime import datetime
import os
from jinja2 import Template



def get_current_time():
  now = datetime.now()
  return now.strftime("%Y_%m_%d_%X")

#
select_id = 26
# scanning information 
result = DB_connect.get_reocrd(id=select_id)


info = {
    "datetime" : result.get("date_time","NULL"),
    "address"  : result.get("target_server_domain","NULL"),
    "ip" : result.get("target_server_ip","NULL"),
    "user_agent" : result.get("tools_user_agent","NULL")
}

#tools config

tools_config = result.get("tools_config",{})

tools_config_results = {}

# for key, value in :

# print(tools_config)
# print(tools_config_results)

#Nmap
nmap_all_result_list = DB_connect.get_one_tool_result(id=select_id, tool_name="nmap")

#whatweb
whatweb_all_result_list = DB_connect.get_one_tool_result(id=select_id, tool_name="whatweb")

for result in whatweb_all_result_list:
    result_structure = {
        'Target URL': result.get('target_url', ''),
        'Web Server': result.get('web_server', ''),
        'OS': result.get('OS', ''),
        'Web technology': result.get('CMS_name', ''),
        'Version': result.get('CMS_version', ''),
        'Recommend Wordlist for Gobuster': result.get('wordlist', '')
    }

whatweb_results = {}
whatweb_results = result_structure

#gobuster
gobuster_results = DB_connect.get_one_tool_result(id=select_id, tool_name="gobuster")

gobuster_results_temp = {}

for index, row in enumerate(gobuster_results):
   gobuster_results_temp[index+1] = {
          "mode": row.get("mode", ""),
          "url": row.get("url", "")
      }

#Nikto
nikto_all_result_list = DB_connect.get_one_tool_result(id=select_id, tool_name="Nikto")

nikto_results = {}
raw_array = []
filtered_array = []

for result in nikto_all_result_list:
    if result.get("type") == "raw":
        raw_array.append(result.get("result"))
        nikto_results[result.get("type")] = raw_array
        
    elif result.get("type") == "filtered":
        filtered_array.append(result.get("result"))
        nikto_results[result.get("type")] = filtered_array

#sqlmap
sqlmap_result = DB_connect.get_one_tool_result(id=select_id, tool_name="sqlmap")
# sqlmap_result = [{'tools': 'sqlmap', 'target_url': 'http://dc8.local/?nid=1', 'database': 'd7db', 'table': 'users', 'datatype': 'columns', 'payload_quantity': '1', 'payload_strength': '1', 'result': {'language': 'varchar(12)', 'access': 'int(11)', 'created': 'int(11)', 'data': 'longblob', 'init': 'varchar(254)', 'login': 'int(11)', 'mail': 'varchar(254)', 'name': 'varchar(60)', 'pass': 'varchar(128)', 'picture': 'int(11)', 'signature': 'varchar(255)', 'signature_format': 'varchar(255)', 'status': 'tinyint(4)', 'theme': 'varchar(255)', 'timezone': 'varchar(32)', 'uid': 'int(10)unsigned'}}, {'tools': 'sqlmap', 'target_url': 'http://dc8.local/?nid=1', 'database': 'd7db', 'table': 'users', 'datatype': 'record', 'payload_quantity': '1', 'payload_strength': '1', 'result': [{'uid': '0', 'data': 'NULL', 'init': '', 'mail': '', 'name': '', 'pass': '', 'login': '0', 'theme': '', 'access': '0', 'status': '0', 'created': '0', 'picture': '0', 'timezone': 'NULL', 'signature': '', 'language': '', 'signature_format': 'NULL'}]}]

sqlmap_data = []
for result in sqlmap_result:
    if result['datatype'] == 'columns':
        columns = [(k, v) for k, v in result['result'].items()]
        sqlmap_data.append({
            'tools': result['tools'],
            'target_url': result['target_url'],
            'database': result['database'],
            'table': result['table'],
            'data_type': result['datatype'],
            'columns': columns,
            'record': None
        })
    elif result['datatype'] == 'record':
        record = [dict(item) for item in result['result']]
        sqlmap_data.append({
            'tools': result['tools'],
            'target_url': result['target_url'],
            'database': result['database'],
            'table': result['table'],
            'data_type': result['datatype'],
            'columns': None,
            'record': record
        })


#xsstrike
xsstrike_results = DB_connect.get_one_tool_result(id=select_id, tool_name="xsstrike")
# [{'tools': 'xsstrike', 'target_url': 'http://xyz.chan2001.com:8881/vulnerabilities/xss_r/?name=13#', 'cookie_info': 'Cookie: PHPSESSID=pe9m2bbtvnru49cncd26cvcl6p; security=low', 'result': ['<test', '<test//', '<test>', '<test x>', '<test x=y', '<test x=y//', '<test/oNxX=yYy//', '<test oNxX=yYy>', '<test onload=x', '<test/o%00nload=x', '<test sRc=xxx', '<test data=asa', '<test data=javascript:asa', '<svg x=y>', '<details x=y//', '<a href=x//', '<emBed x=y>', '<object x=y//', '<bGsOund sRc=x>', '<iSinDEx x=y//', '<aUdio x=y>', '<script x=y>', '<script//src=//', '">payload<br/attr="', '"-confirm``-"', '<test ONdBlcLicK=x>', '<test/oNcoNTeXtMenU=x>', '<test OndRAgOvEr=x>']}]
# xsstrike_data = []
# for result in xsstrike_results:
    
#     pass

template = Template('''
<h1>Scanning information</h1>
<table border="1">
  <tr>
    <th align="left">Date Time</th>
    <td align="left">{{ info.datetime }}</td>
  </tr>
  <tr>
    <th align="left">Target Server Address</th>
    <td align="left">{{ info.address }}</td>
  </tr>
  <tr>
    <th align="left">Target Server IP</th>
    <td align="left">{{ info.ip }}</td>
  </tr>
  <tr>
    <th align="left">User Agent</th>
    <td align="left">{{ info.user_agent }}</td>
  </tr>
</table>

</br></br>

<h1>Tools configuration</h1>
<table border="1">
  <tr>
    <th width=50>Tools</th>
    <th width=50>Status</th>
    <th width=50>Option</th>
  </tr>
{% for key, value in tools_config.items() %}
  <tr>
    <td width=50> {{key}} </td>
    {% for subkey, subvalue in value.items() %}
      <td width=50> {{subkey}} </td>
      <td width=50> {{subvalue}} </td>
    {% endfor %}
  </tr>
{% endfor %}
</table>

</br></br>

<h1>Nmap</h1>
<table border="1">
  <tr>
    {% for key in nmap[0].keys() %}
    <th align="left">{{ key }}</th>
    {% endfor %}
  </tr>
  {% for result in nmap %}
  <tr>
      {% for key, value in result.items() %}
      <td align="left">{{ value }}</td>
      {% endfor %}
  </tr>
  {% endfor %}
</table>

</br></br>

<h1>Whatweb</h1>
<table border="1">
  <tr>
    <th>Information</th>
    <th>Value</th>
  </tr>
  {% for key, value in whatweb_result.items() %}
  <tr>
    <td>{{ key }}</td>
    <td>{{ value }}</td>
  </tr>
  {% endfor %}
</table>
  </tr>
</table>

</br></br>

<h1>Gobuster</h1>
<table border="1">
  <tr>
    <th>Mode</th>
    <th>URL</th>
  </tr>
  {% for result in gobuster %}
  <tr>
    <td>{{ result.mode }}</td>
    <td>{{ result.url }}</td>
  </tr>
  {% endfor %}
</table>

</br></br>

<h1>Nikto</h1>
<table border="1">
  <tr>
    <th>Type</th>
    <th>Information</th>
  </tr>
  {% for value_type, value_informations in nikto.items() %}
    {% for value in value_informations %}
    <tr>
      <td>{{ value_type }}</td>
      <td>{{ value }}</td>
    </tr>
    {% endfor %}
  {% endfor %}
</table>
</br></br>

<h1>SQLMap</h1>
<table border="1">
  <tr>
    <th>Target URL</th>
    <th>Database</th>
    <th>Table</th>
    <th>Data Type</th>
    <th>Columns</th>
    <th>Record</th>
  </tr>
  {% for result in sqlmap_result %}
    <tr>
      <td>{{ result['target_url'] }}</td>
      <td>{{ result['database'] }}</td>
      <td>{{ result['table'] }}</td>
      <td>{{ result['data_type'] }}</td>
      <td>
        {% if result['columns'] %}
          <ul>
            {% for column in result['columns'] %}
              <li>{{ column[0] }}: {{ column[1] }}</li>
            {% endfor %}
          </ul>
        {% else %}
          -
        {% endif %}
      </td>
      <td>
        {% if result['record'] %}
          <ul>
            {% for item in result['record'] %}
              <li>{{ item }}</li>
            {% endfor %}
          </ul>
        {% else %}
          -
        {% endif %}
      </td>
    </tr>
  {% endfor %}
</table>
    
</br></br>

{% autoescape true %}
<h1>XSStrike</h1>
<table border="1">
  <tr>
    <th>Target URL</th>
    <th>Results</th>
  </tr>
  {% for result in xsstrike_data %}
    {% if result['result'] %}
      <tr>
        <td>{{ result['target_url'] }}</td>
        <td>
          {% for item in result['result'] %}
            {{ item }}<br>
          {% endfor %}
        </td>
      </tr>
    {% endif %}
  {% endfor %}
</table>
{% endautoescape %}
''' )

table_html = template.render(info=info,tools_config=tools_config, nmap=nmap_all_result_list, gobuster=gobuster_results, whatweb_result = whatweb_results, nikto=nikto_results, sqlmap_result=sqlmap_data, xsstrike_data=xsstrike_results)
# print(table_html)
temp_path = f'{os.path.dirname(__file__)}/temp.html'
with open(temp_path, 'w') as f:
    f.write(table_html)

pdf.from_file(temp_path, f"{os.path.dirname(__file__)}/output/{get_current_time()}.pdf")