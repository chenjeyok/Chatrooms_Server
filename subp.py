import subprocess
try:
    print subprocess.check_output('exec bash', shell=True)
except Exception, emsg:
    print str(emsg)
    