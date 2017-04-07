def captialize_name(name):
    return ' '.join([(s[0].upper() + s[1:]) if len(s) > 0 else '' for s in name.split(' ')])