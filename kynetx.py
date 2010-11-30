import httplib, urllib, json, re, socket

class kynetx:
  """A library to raise Kynetx events"""

  def __init__(self,app_id):
    self.appid = app_id
    self.directives = []
    self.socket = None
    self.token = 0

  def open_socket(self, params = {"url":"caandb.com","port":8000}):
    if self.socket:
      self.socket.shutdown(socket.SHUT_RDWR)
      self.socket.close()
      del self.socket
    self.socket = socket.create_connection((params['url'],params['port']))
    self.socket_file = self.socket.makefile("Uw+")
    data_string = self.socket_file.readline()
    self.token = json.loads(data_string)['token']

  def get_token(self):
    return self.token

  def get_socket_line(self):
    return self.socket_file.readline()

  def get_socket_lines(self):
    return self.socket_file.readlines()

  def set_token(self, new_token):
    if(new_token != self.token):
      to_send = {};
      to_send['token'] = new_token;
      self.socket_file.write(json.dumps(to_send)+'\r\n')
      self.socket_file.flush()
      data_string = self.socket_file.readline()

      print data_string

      response = json.loads(data_string)

      if(response['error'] != "none"):
        raise Exception("token change", response['error'])
      else:
        self.token = new_token

  def raise_event(self,domain,event_name, params = {}):
    params_encoded = urllib.urlencode(params)

    print '/blue/event/'+domain+'/'+event_name+'/'+self.appid
    try:
      kynetx_connection = httplib.HTTPConnection('cs.kobj.net')
      kynetx_connection.request("GET", '/blue/event/'+domain+'/'+event_name+'/'+self.appid + '?' + params_encoded)
      directives = re.sub('^//.*','',kynetx_connection.getresponse().read(),re.S)
      del kynetx_connection
    except:
      print "Much puke."
      directives = '{"directives":[]}'

    print directives
    self.parse_directives(directives)
    return directives

  def parse_directives(self,directives):
    try:
      data = json.loads(directives)['directives']
    except:
      data = []
    self.directives = []
    temp = {}
    for directive in data:
      try:
        temp['txn_id'] = directive['meta']['txn_id']
      except:
        temp['txn_id'] = 0
      temp['action'] = directive['name']
      temp['options'] = directive['options']
      self.directives.append(temp)
