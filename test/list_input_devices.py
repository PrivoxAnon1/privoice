from framework.util.utils import execute_command
from pprint import pprint

def get_devices(cmd):
    res = execute_command(cmd)
    res = res[7:]
    lines = res.split("\n")
    devices = []
    for line in lines:
        if line:
            if ord(line[0]) != 32 and not line.startswith("STDERR:"):
                line = line.replace("CARD=","")
                line = line.replace("DEV=","")
                devices.append(line)

    return devices

cmd = "arecord -L"
input_devices = get_devices(cmd)

cmd = "aplay -L"
output_devices = get_devices(cmd)

print("""
Only use one of these values if your mic is not working using the default value.
Enter one of the names below as your input device in the yava.yml file.
     """)
pprint(input_devices)


print("""
Only use one of these values if your speaker is not working using the default value.
Enter one of the names below as your output device in the yava.yml file.
For example: 
    OutputDeviceName: default
     """)
pprint(output_devices)



