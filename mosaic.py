#!/usr/bin/python

import subprocess
import sys
import re
from enum import IntEnum
import itertools
import argparse


# Derived from input.h in Linux kernel
class Input(object):

    class Type(IntEnum):
        SYN               = int( '0x00', 16)
        KEY               = int( '0x01', 16)
        ABS               = int( '0x03', 16)
        MSC               = int( '0x04', 16)

    class MSC(IntEnum):
        SCAN              = int( '0x04', 16)

    class SYN(IntEnum):
        REPORT            = int( '0x00', 16)
        CONFIG            = int( '0x01', 16)
        MT_REPORT         = int( '0x02', 16)
        DROPPED           = int( '0x03', 16)

    class KEY(IntEnum):
        BTN_TOOL_PEN      = int('0x140', 16)
        BTN_TOOL_RUBBER   = int('0x141', 16)
        BTN_TOOL_BRUSH    = int('0x142', 16)
        BTN_TOOL_PENCIL   = int('0x143', 16)
        BTN_TOOL_AIRBRUSH = int('0x144', 16)
        BTN_TOOL_FINGER   = int('0x145', 16)
        BTN_TOOL_MOUSE    = int('0x146', 16)
        BTN_TOOL_LENS     = int('0x147', 16)
        BTN_TOUCH         = int('0x14a', 16)

    class ABS(IntEnum):
        X                 = int( '0x00', 16)
        Y                 = int( '0x01', 16)
        PRESSURE          = int( '0x18', 16)
        DISTANCE          = int( '0x19', 16)
        TOOL_WIDTH        = int( '0x1c', 16)
        MT_SLOT           = int('0x2f', 16)
        MT_TOUCH_MAJOR    = int('0x30', 16)
        MT_TOUCH_MINOR    = int('0x31', 16)
        MT_WIDTH_MAJOR    = int('0x32', 16)
        MT_WIDTH_MINOR    = int('0x33', 16)
        MT_ORIENTATION    = int('0x34', 16)
        MT_POSITION_X     = int('0x35', 16)
        MT_POSITION_Y     = int('0x36', 16)
        MT_TOOL_TYPE      = int('0x37', 16)
        MT_BLOB_ID        = int('0x38', 16)
        MT_TRACKING_ID    = int('0x39', 16)
        MT_PRESSURE       = int('0x3a', 16)
        MT_DISTANCE       = int('0x3b', 16)
        MT_TOOL_X         = int('0x3c', 16)
        MT_TOOL_Y         = int('0x3d', 16)
        MAX               = int('0x3f', 16)


class Device(object):

    def __init__(self, serial_num):
        self.serial_num = serial_num
        self.init_display = None
        self.cur_display = None
        self.app_display = None
        self.rotated = None
        self.init_touchscreen = None
        self.cur_touchscreen = None
        self.app_touchscreen = None
        self.menu_touchscreen = None


class Screen(object):

    def __init__(self, xmax=0, ymax=0):
        self.xmax = int(xmax)
        self.ymax = int(ymax)
        self.orientation = "landscape" if xmax > ymax else "portrait"

    def __str__(self):
        return "%sx%s %s" % (self.xmax, self.ymax, self.orientation)


class Event(object):

    def __init__(self, ev_time, ev_type, ev_code, ev_value):
        self.ev_time = ev_time
        self.ev_type = ev_type
        self.ev_code = ev_code
        self.ev_value = ev_value

    def __eq__(self, other):
        if self.ev_type == other.ev_code and self.ev_value == other.ev_value:
            if (self.ev_type == Input.Type.KEY and self.ev_code == Input.KEY.BTN_TOUCH):
#or (self.ev_type == Input.Type.ABS and self.ev_type == Input.ABS.MT_TRACKING_ID):
                return self.ev_value == other.ev_value
            else:
                return True
        else:
            return False

    def __str__(self):
        return "%d,%d,%d,%s" % (self.ev_time, self.ev_type, self.ev_code, self.ev_value)


def shell(args):
    """ TODO """
    shell = subprocess.Popen(args, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
    stdout, stderr = shell.communicate()
    if shell.returncode != 0:
        print >> sys.stderr, stderr
        sys.exit(1)
    return ( line for line in stdout.split('\r\n') )


def adb_devices():
    """ TODO """
    adb_args = ['adb', 'devices']
    return [ serial_num for idx, serial_num in 
            enumerate(' '.join(shell(adb_args)).split()) 
            if idx > 3 and idx % 2 == 0 ]
    

def adb_shell(serial_num, cmd):
    """ TODO """
    adb_args = ['adb', '-s', serial_num, 'shell'] + cmd.split()
    stdout = shell(adb_args)
    return ( line for line in stdout )

def adb_push(serial_num, filename):
    """ TODO """
    adb_args = ['adb', '-s', serial_num, 'push', filename, '/sdcard/' ]
    stdout = shell(adb_args)
    return ( line for line in stdout )


def get_display_info(output, device):
#    output = adb("dumpsys window").split("\r\n")
    for line in output:
        if 'init' in line and 'cur' in line and 'app' in line:
            r = re.match(r'.*init=([0-9]+)x([0-9]+).*cur=([0-9]+)x([0-9]+)'
                         r'.*app=([0-9]+)x([0-9]+).*', line, re.M | re.I)
            device.init_display = Screen(r.group(1), r.group(2))
            device.cur_display = Screen(r.group(3), r.group(4))
            device.app_display = Screen(r.group(5), r.group(6))
            device.rotated = device.cur_display.orientation != device.init_display.orientation
            

def get_touchscreen_info(output, device):
#    output = adb("getevent -lp").split("\r\n")
    for line in output:
        if 'ABS_MT_POSITION_X' in line or 'ABS_X' in line:
            r = re.match(r'.*max ([0-9]+).*', line, re.M | re.I)
            touchscreen_width = r.group(1)
        if 'ABS_MT_POSITION_Y' in line or 'ABS_Y' in line:
            r = re.match(r'.*max ([0-9]+).*', line, re.M | re.I)
            touchscreen_height = r.group(1)
    device.init_touchscreen = Screen(touchscreen_width, touchscreen_height)
    device.cur_touchscreen = Screen()
    device.cur_touchscreen.xmax = device.init_touchscreen.xmax if not device.rotated \
                                  else device.init_touchscreen.ymax
    device.cur_touchscreen.ymax = device.init_touchscreen.ymax if not device.rotated \
                                  else device.init_touchscreen.xmax
    device.app_touchscreen = Screen()
    device.app_touchscreen.xmax = ((device.cur_touchscreen.xmax * device.app_display.xmax) /
                                   device.cur_display.xmax)
    device.app_touchscreen.ymax = ((device.cur_touchscreen.ymax * device.app_display.ymax) /
                                    device.cur_display.ymax)
    device.menu_touchscreen = Screen()
    device.menu_touchscreen.xmax = device.cur_touchscreen.xmax - device.app_touchscreen.xmax
    device.menu_touchscreen.ymax = device.cur_touchscreen.ymax - device.app_touchscreen.ymax


def get_touch_device(output):
    for line in output:
        if 'add' in line:
            r = re.match(r'add device.*: (.*)', line, re.M | re.I)
            device = r.group(1)
        elif '0039  :' in line:
            break
    return device


def line_is_event(line):
    return '/dev/input/event' in line and 'add' not in line
#    return line.find('/dev/input/event') != -1 and line.find('[') != -1


def extract_tokens(line):
    tokens = line.rstrip('\n').split()
    return tokens[1:] if tokens[0] == "[" else tokens


def extract_time(raw_time):
    return int(raw_time.replace('.', '').replace(']', '')
            .replace('[', '').replace('-','').replace(':',''))*1000


def extract_device(raw_event):
    return int(raw_event.replace('/dev/input/event', '').replace(':', ''))


def extract_type(raw_type):
    return int(raw_type, 16)


def extract_code(raw_code):
    return int(raw_code, 16)


def extract_value(raw_value):
    return int(raw_value, 16)


def valid(touchscreen_device, input_event_line):
    not_touchscreen_registration = "add" not in input_event_line
    is_touchscreen_input_event = touchscreen_device + ':' in input_event_line
    return not_touchscreen_registration and is_touchscreen_input_event


def parse_device(line):
        tokens = extract_tokens(line)
        return Event(int(tokens[0]), extract_type(tokens[1]), 
                extract_code(tokens[2]), extract_value(tokens[3]))


def classify(event):
    if Input.Type(event.ev_type) is Input.Type.SYN:
        return (Input.Type.SYN, Input.SYN(event.ev_code))
    elif Input.Type(event.ev_type) is Input.Type.KEY:
        return (Input.Type.KEY, Input.KEY(event.ev_code))
    elif Input.Type(event.ev_type) is Input.Type.ABS:
        return (Input.Type.ABS, Input.ABS(event.ev_code))

def encode(event):
    return (classify(event)[0], classify(event)[1] , event.ev_value if classify(event) == (Input.Type.KEY, Input.KEY.BTN_TOUCH) or 
            (classify(event)[1] == Input.ABS.MT_TRACKING_ID and event.ev_value == int('0xffffffff',16)) 
            else 0 )

def get_interactions(input_event_file):
    """ TODO """
    event_stream = filter(lambda input_event_line: '#' not in input_event_line, input_event_file)
    touchscreen_events = map(lambda input_event_line: parse_device(input_event_line), event_stream)
    splits = [ -1 ] + [ idx for idx, event in enumerate(touchscreen_events) 
                       if event.ev_type == Input.Type.SYN and event.ev_code == Input.Type.SYN ]
    touchscreen_interactions = [ touchscreen_events[splits[i]+1:splits[i+1]+1] 
                                for i in range(0,len(splits)-1) ]
    return touchscreen_interactions


def get_ref_interactions(event_stream):
    """ TODO """

    touchscreen_interactions = get_interactions(event_stream)

    press = touchscreen_interactions[0]
    moves = [ event for interaction in touchscreen_interactions[1:-1] for event in interaction ]
    release = touchscreen_interactions[-1]
    return press, moves, release


def virtualize(args):
    """ TODO """
    serial_num = get_serial_num(args)
    touchscreen_device = get_touch_device(adb_shell(serial_num, 'getevent -p'))

    device = Device(serial_num)
    get_display_info(adb_shell(serial_num, "dumpsys window"), device)
    get_touchscreen_info(adb_shell(serial_num, "getevent -lp"), device)
    
    # ref_press, ref_moves, ref_release = get_ref_interactions(open(serial_num + '.one_finger_swipe'))
    ref_press, ref_moves, ref_release = get_ref_interactions(open(args.calibration_file))
    ref_press_encoded = map(lambda event: encode(event), ref_press) 
    ref_moves_encoded = map(lambda event: encode(event), ref_moves) 
    ref_release_encoded = map(lambda event: encode(event), ref_release) 

    #print [ str(event) for event in ref_press_encoded ]
    #print [ str(event) for event in ref_moves ]
    #print [ str(event) for event in ref_release_encoded ]

    uniq_press = set(ref_press_encoded) - set(ref_moves_encoded) - set(ref_release_encoded)
    uniq_release = set(ref_release_encoded) - set(ref_moves_encoded) - set(ref_press_encoded)

#    print [ str(event) for event in uniq_press ]
#    print [ str(event) for event in uniq_release ]

    input_file = open(args.input_file, 'r')
    event_stream = filter(lambda line: '#' not in line, input_file.read().splitlines())

    touchscreen_interactions = get_interactions(event_stream)
    
    print '# Orientation: %s' % device.cur_display.orientation
    print '#'
    print '# Time Action X Y'

    last_time = None
    for interaction in touchscreen_interactions:
        interaction_set = set(map(lambda event: encode(event), interaction))
        if 4 * len(set.intersection(set(interaction_set),uniq_press)) > 3 * len(uniq_press):
            action = 'press'
        elif 4 * len(set.intersection(set(interaction_set),uniq_release)) > 3 * len(uniq_release):
            action = 'release'
        else:
            action = 'move'
        xpos = None
        ypos = None
        times = [ event.ev_time for event in interaction ]
        time = max(times)
        for event in interaction:
             if classify(event) == (Input.Type.ABS, Input.ABS.MT_POSITION_X) or classify(event) == (Input.Type.ABS, Input.ABS.X):
                 if not device.rotated:
                     xpos = ((100.0 * float(event.ev_value)) /
                            float(device.app_touchscreen.xmax))
                 else:
                     ypos = ((100.0 * (float(device.app_touchscreen.ymax) -
                             float(event.ev_value) +
                             float(device.menu_touchscreen.ymax))) /
                             float(device.app_touchscreen.ymax))
             elif classify(event) == (Input.Type.ABS, Input.ABS.MT_POSITION_Y) or classify(event) == (Input.Type.ABS, Input.ABS.Y):
                 if not device.rotated:
                     ypos = ((100.0 * float(event.ev_value)) /
                             float(device.app_touchscreen.ymax))
                 else:
                     xpos = ((100.0 * float(event.ev_value)) /
                             float(device.app_touchscreen.xmax))
        if not (action == 'move' and xpos is None and ypos is None):
            pretty_interaction = [ "%d" % int(time - last_time)  if last_time is not None else str(0) ] 
            last_time = time
            pretty_interaction += [ action ]
            pretty_interaction += [ str(xpos) if xpos is not None else '--' ]
            pretty_interaction += [ str(ypos) if ypos is not None else '--' ]
            print '\t'.join(pretty_interaction)
 

def translate(args):
    """ TODO """
    serial_num = get_serial_num(args)
    touchscreen_device = get_touch_device(adb_shell(serial_num, 'getevent -p'))
    touchscreen_device = int(touchscreen_device.replace('/dev/input/event','').replace(':','')) # hack for now 

    device = Device(serial_num)
    get_display_info(adb_shell(serial_num, "dumpsys window"), device)
    get_touchscreen_info(adb_shell(serial_num, "getevent -lp"), device)

    ref_press, ref_moves, ref_release = get_ref_interactions(open(args.calibration_file))
    #print [ str(event) for event in ref_press ]
    #print [ str(event) for event in ref_moves ]
    #print [ str(event) for event in ref_release ]

    input_file = open(args.input_file, 'r')
    interaction_stream = filter(lambda line: '#' not in line, input_file.read().splitlines())
    tracking_id = 34 
    events = []
    for interaction in interaction_stream:
        tokens = interaction.split()
        if tokens[1] == 'press':
            for event in ref_press:
                event.ev_time = 1
                if classify(event) == (Input.Type.ABS, Input.ABS.MT_POSITION_X) or classify(event) == (Input.Type.ABS, Input.ABS.X):
                    event.ev_value = (float(tokens[2]) * device.app_touchscreen.xmax) / 100.0 if not device.rotated \
                                     else device.menu_touchscreen.ymax + device.app_touchscreen.ymax - (float(tokens[3]) * device.app_touchscreen.ymax) / 100.0
                elif classify(event) == (Input.Type.ABS, Input.ABS.MT_POSITION_Y) or classify(event) == (Input.Type.ABS, Input.ABS.Y):
                    event.ev_value = (float(tokens[3]) * device.app_touchscreen.ymax) / 100.0 if not device.rotated \
                                      else  (float(tokens[2]) * device.app_touchscreen.xmax) / 100.0
                elif classify(event) == (Input.Type.ABS, Input.ABS.MT_TRACKING_ID):
                    event.ev_value = tracking_id
                    tracking_id += 1
#            if int(tokens[0]) != 0:
#                ref_press[-1].ev_time = int(tokens[0])
            ref_press[0].ev_time = int(tokens[0])
            for event in ref_press:
                tmp =  "%d,%d,%d,%d,%d" % (event.ev_time, touchscreen_device, event.ev_type, event.ev_code, event.ev_value)
                events.append(tmp)
        elif tokens[1] == 'release':
            for event in ref_release:
                event.ev_time = 1
            ref_release[0].ev_time = int(tokens[0])
            for event in ref_release:
                tmp = "%d,%d,%d,%d,%d" % (event.ev_time, touchscreen_device, event.ev_type, event.ev_code, event.ev_value)
                events.append(tmp)
        else:
            time = int(tokens[0])
            if (tokens[2] != '--' and not device.rotated) or (tokens[3] != '--' and device.rotated):
                tmp = "%d,%d,%d,%d,%d" % (time, touchscreen_device, Input.Type.ABS, Input.ABS.MT_POSITION_X, 
                    (float(tokens[2]) * device.app_touchscreen.xmax) / 100.0 if not device.rotated \
                     else device.menu_touchscreen.ymax + device.app_touchscreen.ymax - (float(tokens[3]) * device.app_touchscreen.ymax) / 100.0)
                events.append(tmp)
                time = 1
            if (tokens[2] != '--' and device.rotated) or (tokens[3] != '--' and not device.rotated):
                tmp = "%d,%d,%d,%d,%d" % (time, touchscreen_device, Input.Type.ABS, Input.ABS.MT_POSITION_Y,
                   (float(tokens[3]) * device.app_touchscreen.ymax) / 100.0 if not device.rotated \
                    else  (float(tokens[2]) * device.app_touchscreen.xmax) / 100.0)
                events.append(tmp)
            tmp = "%d,%d,%d,%d,%d" % (1, touchscreen_device, Input.Type.SYN, Input.SYN.REPORT, 0)
            events.append(tmp)
    print len(events)
    print '\n'.join(events)

def replay(args):
    """ TODO """
    serial_num = get_serial_num(args)
    print '\n'.join(adb_push(serial_num,args.input_file))
    adb_shell(serial_num,'su -c /data/reran/reran /sdcard/' + args.input_file)


def get_serial_num(args):
    """ TODO """
    if args.target_serial_num is not None:
        serial_num = args.target_serial_num 
    else:
        connected_devices = adb_devices()
        if len(connected_devices) == 1:
            serial_num =  connected_devices[0]
        else:
            print >> sys.stderr, 'Error: More than one device and emulator ' \
                                 'connected.'
            sys.exit(1)
    return serial_num


def adb_getevent(serial_num):
    adb_args = ['adb', '-s', serial_num, 'shell', 'getevent', '-tt']
    adb = subprocess.Popen(adb_args, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
    try:
        while True:
            yield adb.stdout.readline().strip()
    except KeyboardInterrupt:
        return


def record(args):
    """ TODO """
    serial_num = get_serial_num(args)
    touchscreen_device = get_touch_device(adb_shell(serial_num, 'getevent -p'))

    device = Device(serial_num)
    get_display_info(adb_shell(serial_num, "dumpsys window"), device)
    get_touchscreen_info(adb_shell(serial_num, "getevent -lp"), device)

    print "# Default Display: %s" % device.init_display
    print "# Current Display: %s" % device.cur_display
    print "# App Display: %s" % device.app_display
    print "# Rotated: %s" % str(device.rotated)
    print "# Default Touchscreen: %s" % device.init_touchscreen
    print "# Current Touchscreen: %s" % device.cur_touchscreen
    print "# App Touchscreen: %s" % device.app_touchscreen
    print "# Menu Touchscreen: %s" % device.menu_touchscreen
    print "#"
    print "# Time Type Code Value"

    touchscreen_events = itertools.ifilter(lambda input_event_line: 
                 valid(touchscreen_device, input_event_line),
                 adb_getevent(serial_num))

    for event in touchscreen_events:
        tokens =  extract_tokens(event)
        print extract_time(tokens[0]),tokens[2],tokens[3],tokens[4]


def parse_args():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('-a','--action', dest='action', 
                        help='action to perform', 
                        default=None, metavar='')
    
    parser.add_argument('-c','--calib-file', dest='calibration_file', 
                        help='calibration file', 
                        default=None, metavar='')


    parser.add_argument('-t','--target-serial-num', dest='target_serial_num', 
                        help='target device serial number', 
                        default=None, metavar='')

    parser.add_argument('-r','--ref-serial-num', dest='ref_serial_num', 
                        help='reference device serial number', 
                        default=None, metavar='')
    parser.add_argument('-i','--input-file', dest='input_file', 
                        help='input file', 
                        default=None, metavar='')

    return parser.parse_args()


def main():

    args = parse_args()

    if args.action == 'record':
        record(args)
    elif args.action == 'virtualize':
        virtualize(args)
    elif args.action == 'translate':
        translate(args)
    elif args.action == 'replay':
        replay(args)

    sys.exit(0)

main()
