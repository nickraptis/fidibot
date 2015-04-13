# Author: Nick Raptis <airscorp@gmail.com>
"""Collection of auth functions for the bot"""

class AdminAuth(object):
    def __init__(self, password):
        self.password = password
        self.auth_pool = set()

    def authenticate(self, password):
        return bool(self.password) and password == self.password

    def is_admin(self, username):
        return username in self.auth_pool

    def add(self, username):
        self.auth_pool.add(username)

    def remove(self, username):
        if username in self.auth_pool:
            self.auth_pool.remove(username)


if __name__ == '__main__':
    # Test the AdminAuth class
    admins = AdminAuth(None)
    assert admins.authenticate(None) == False
    assert admins.authenticate("password") == False
    
    admins = AdminAuth("password")
    assert admins.authenticate(None) == False
    assert admins.authenticate("wrongpassword") == False
    assert admins.authenticate("password") == True
    
    assert admins.is_admin("user") == False
    admins.add("user")
    assert admins.is_admin("user") == True
    admins.add("user")
    admins.remove("user")
    assert admins.is_admin("user") == False
    admins.remove("user")
    
    print "Everything in order"
