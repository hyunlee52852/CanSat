from datetime import datetime
t = datetime.today().isoformat(sep=' ', timespec='milliseconds')
print(t)