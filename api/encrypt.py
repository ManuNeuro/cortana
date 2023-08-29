from cryptography.fernet import Fernet
import numpy as np
from os.path import exists, join
import json 

# generate a key for encryption and decryption
# You can use fernet to generate
# the key or use random key generator
# here I'm using fernet to generate the key.

def encrypt_key(secret_key, key=None, path='', name='encrypted_key'):
    
    if (key is None):
        path_file = join(path, name)
        if not exists(path_file+'.npy'):
            key = Fernet.generate_key()
            np.save(path_file+'.npy', key)
        else:
            key = str(np.load(path_file+'.npy'))[1:]
    
    # Instance the Fernet class with the key
    fernet = Fernet(key)
    
    # then use the Fernet class instance
    # to encrypt the string string must
    # be encoded to byte string before encryption
    encMessage = str(fernet.encrypt(secret_key.encode()))[1:]
    decMessage = fernet.decrypt(encMessage.encode()).decode()
    if decMessage != secret_key:
        raise Exception('Issues when encrypting, source and decoded messages are not the same')
        
    # Save in a json the encrypted key    
    with open(path_file+'.json', 'w') as file:
        json_string = json.dumps({name:encMessage}, default=lambda o: o.__dict__, sort_keys=True, indent=2)
        file.write(json_string)
    
    return encMessage

def decrypt_key(path='', name='encrypted_key'):
    
    path_file = join(path, name)
    if exists(path_file+'.npy'):
        key = str(np.load(path_file+'.npy'))[1:]
    else:
        raise Exception("Can't decode the message, the path is invalid. Provide the correct path.")
    
    with open(path_file+'.json', "r") as output:
        dic_api = json.load(output)
        
    encMessage = dic_api[name]
    fernet = Fernet(key)
    decMessage = fernet.decrypt(encMessage.encode()).decode()
    return decMessage
