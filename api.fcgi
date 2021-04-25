#!/home/httpd/vhosts/re86.ru/subdomains/api/httpdocs/venv/Scripts/python.exe
import sys
sys.path.append('/home/httpd/vhosts/re86.ru/subdomains/api/httpdocs')

from flup.server.fcgi import WSGIServer
from run import app

if __name__ == '__main__':
    WSGIServer(app).run()
