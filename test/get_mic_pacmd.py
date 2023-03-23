import re, os
import subprocess


def get_mic_level():
    cmd_str = "pacmd list-sources"
    output = str(subprocess.Popen(cmd_str ,shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT).communicate()[0])
    output = output.split("\\n")  # split on new lines
    state = 'idle'
    for line in output:
        line = line.replace("\\t","")  # remove tabs

        if state == 'active':
            # looking for volume line looks like this 
            # volume: front-left: 23000 /  35% / -27.29 dB,   front-right: 23000 /  35% / -27.29 dB
            if line.find("volume: ") > -1:
                line = line.split(",")
                return re.search('[0-9]+', line[0]).group()

        if line.find("* index:") > -1:
            state = 'active'

    return -1   # error, value not found

vol = get_mic_level()
print(vol)

