from xmlrpclib import ServerProxy, Fault
from client import randomString
from node import Node, UNHANDLED
from threading import Thread
from time import sleep
import sys
import wx

SECRET_LENGTH = 100
HEAD_START = 0.1 #Seconds

    
class Client(wx.App):
    
    def __init__(self, url, dirname, urlfile):
        super(Client, self).__init__()
        self.secret = randomString(SECRET_LENGTH)
        node = Node(url, dirname, self.secret)
        thread = Thread(target=node._start)
        thread.setDaemon(1)
        thread.start()
        sleep(HEAD_START)
        self.server = ServerProxy(url)
        for line in open(urlfile):
            line = line.strip()
            self.server.hello(line)
            
    def OnInit(self):
        """
        Sets up the GUI. Creates a window, a text field, and a button, and lays them out.
        Binds the submit button to self.fetchHandler
        """
        win = wx.Frame(None, title="File Sharing Client", size=(400, 100))
        bkg = wx.Panel(win)
        
        self.input = input = wx.TextCtrl(bkg)
        
        submit = wx.Button(bkg, label="Fetch", size=(80, 25))
        submit.Bind(wx.EVT_BUTTON, self.fetchHandler)
        
        hbox = wx.BoxSizer()
        hbox.Add(input, proportion=1, flag=wx.ALL | wx.EXPAND, border=10)
        hbox.Add(submit, flag=wx.TOP | wx.BOTTOM | wx.RIGHT, border=10)
        
        vbox = wx.BoxSizer(wx.VERTICAL)
        vbox.Add(hbox, proportion=0, flag=wx.EXPAND)
        
        bkg.SetSizer(vbox)
        
        win.Show()
        
        return True
            
    def fetchHandler(self, event):
    
        query = self.input.GetValue()
        try:
            self.server.fetch(query, self.secret)
        except Fault as f:
            if f.faultCode != UNHANDLED:
                raise
            print("Couldn't find the file %s" % query)
        
def main():
    urlfile, directory, url = sys.argv[1:]
    client = Client(url, directory, urlfile)
    client.MainLoop()
    
if __name__ == '__main__':
    main()