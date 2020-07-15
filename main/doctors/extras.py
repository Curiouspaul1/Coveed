#! python3 

import jwt

class Token:
    def __init__(self,type,secret,token):
        self.type = type
        self.secret = secret
        if self.type == 'refresh':
            self.token = jwt.encode({''})
        elif self.type == 'access':
            self.token = jwt.encode({})

    def getIdentity(self):
        """"
        Takes in token and secre_key,returns decrypted token with payload
        """"
        result = jwt.decode(self,self.secret)
        return result['doc_id']

