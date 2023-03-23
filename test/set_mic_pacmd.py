import re, os, sys
import subprocess

def set_mic_level(new_volume):
    # usually between 0-65535
    cmd_str = "pacmd list-sources | grep '\*'"
    output = str(subprocess.Popen(cmd_str ,shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0])
    indx = re.sub('[^\d]','', output)
    cmd = "pacmd set-source-volume %s %s" % (indx,new_volume)
    os.system(cmd)


if len(sys.argv) < 2:
    quit()

set_mic_level(sys.argv[1])
