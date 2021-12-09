from flask import redirect, render_template, request, session
from functools import wraps
from hashlib import md5

def login_required(f):
    
    @wraps(f)
    def decoreted_function(*args, **kwargs):
        
        if session.get("userId") is None:
            return redirect("/login")
        return f(*args, **kwargs)

    return decoreted_function

def hashing(password): 
    bitwise = bytes(f"{password}", 'utf-8')
    return md5(bitwise).hexdigest()
