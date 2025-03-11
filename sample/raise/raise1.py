import traceback
 
try:
    raise Exception
except:
    traceback.print_exc()