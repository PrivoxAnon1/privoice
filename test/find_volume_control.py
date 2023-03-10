from framework.util.utils import execute_command

cmd = "cat /proc/asound/cards"
res = execute_command(cmd)
res = res.split("STDERR")[0]
res = res[7:]  # remove STDOUT:
lines = res.split("\n")
card_nums = []
for line in lines:
    line = line[1:].strip()
    if line:
        card_num = line[0:2]
        try:
            card_nums.append(int(card_num))
        except:
            pass

# find a working master
working_card = -1
for card in card_nums:
    cmd = "amixer -c %s sget 'Master'" % (card,)
    res = execute_command(cmd)
    res = res.split("\n")[0]
    if res.startswith("STDOUT:"):
        res = res[7:]
        if len(res) > 2:
            print("Found card %s ---> %s" % (card, res))
            working_card = card
            break

if working_card == -1:
    print("No master control found")
else:
    cmd = "amixer -c %s sset Master 75%s" % (working_card,'%')
    print("To change your volume use this command %s" % (cmd,))


