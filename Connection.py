#!/usr/bin/env python3

import socket
import time
import select

class Connection:
    """
    Establishes a connection to a server,
    then keeps it up (TODO!),
    or reconnects if needed.

    You should only ever need the method run()
    """
    def __init__ (self, server, port, nicknames, realname, ident, admins):
        """
        Parameters:
        -----------
        server:     string (e. g. "chat.freenode.net")
        port:       integer (e. g. 6667)
        nicknames:  tuple of strings (e. g. ("iobot", "i0bot"))
        realname:   string (e. g. "iobot")
        ident:      string (e. g. "iobot")
        admins:     tuple of strings (
                    e. g. your nicknames on the server:
                    ("terry", "john", "michael")
        """
        self.SERVER = server
        self.PORT = port
        self.NICKNAMES = nicknames
        self.reconnects = 0
        self.REALNAME = realname
        self.IDENT = ident
        self.ADMINS = admins
        self.lastping = time.time()
        self.pingtimeout = 500
        self.sleep_before_reconnect = 10
        self.connected = False

    def run (self):
        """
        If you set up this class properly, this should just establish
        and keep up a connection to an IRC server of your choosing.
        """
        run = True
        stub = ''
        while run:
            if not self.connected:
                try:
                    if not self.reconnects == 0:
                        print ("*** Waiting %i seconds, \
                                then reconnecting [%i] ***" % \
                                (self.sleep_before_reconnect, \
                                self.reconnects))
                        self.s.close ()
                        self.lastping = time.time()
                    self.nickname = self.NICKNAMES[self.reconnects % \
                            len(self.NICKNAMES)]
                    print ("Connecting to " + self.SERVER)
                    self.connected = True
                    self.connect()
                    for a in self.ADMINS:
                        msg = "PRIVMSG " + a + " :Connected successfully! [%i]\n" % self.reconnects
                        self.send_to_server(msg)
                    self.reconnects += 1
                except Exception as e:
                    self.connected = False
                    print ("Something went wrong while connecting:")
                    raise e
            stream = self.listen (4096)
            if not stream == "":
                print (stream)
                self.parse(stream)
            if self.lastping + self.pingtimeout < time.time():
                self.connected = False
                print ("*** Lost connection ***")
    
    def connect (self):
        self.s = socket.socket()
        self.s.connect((self.SERVER, self.PORT))
        connection_msg = \
                "NICK " + self.nickname + "\n" + \
                "User " + self.IDENT + " " + \
                self.SERVER + " bla: " + \
                self.REALNAME + "\n"
        self.send_to_server(connection_msg)

    def listen (self, chars):
        s_ready = select.select([self.s],[],[],10)
        if s_ready:
            return self.s.recv(chars).decode("UTF-8")

    def parse (self, stream):
        lines = stream.split("\n")
        for l in lines:
            if l[:4] == "PING":
                pong = "PONG" + l[4:] + "\n"
                self.send_to_server(pong)
                self.lastping = time.time()
                print (pong)

    def send_to_server(self, message):
        self.s.send(message.encode("UTF-8"))

if __name__ == '__main__':
    print ("*** This file shouldn't be executed. ***")
