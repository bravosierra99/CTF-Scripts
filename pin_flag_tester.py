import subprocess, string, argparse, sys, logging 
DEFAULT_CHARSET = string.letters+string.digits+string.punctuation
PRINTABLE_CHARSET = string.printable
WHITESPACE_CHARSET = string.letters+string.digits+string.whitespace
charset = DEFAULT_CHARSET
DEFAULT_FLAG_BUILDER = "flag{" 
flag_builder = DEFAULT_FLAG_BUILDER
DEFAULT_INSCOUNT_FILENAME = "inscount.log"
inscount_filename = DEFAULT_INSCOUNT_FILENAME
target_executable = None
DEFAULT_FLAG_TERMINATOR = '}'
flag_terminator = DEFAULT_FLAG_TERMINATOR 
DEFAULT_PIN_PATH = '/opt/pin'
pin_path = DEFAULT_PIN_PATH
pin_location = pin_path + '/pin'
tool_path = pin_path + '/source/tools/ManualExamples/obj-ia32'
tool_name = 'inscount0.so'
tool_location = tool_path+'/'+tool_name
flag_length = len(flag_builder)
enumeration_tolerence = 50
enumerate_flag = False
build_flag = False
build_flag_length = False
DEFAULT_FILL_CHAR = 'z'
fill_char = DEFAULT_FILL_CHAR
flag_length = 0

YELLOW_COLOR = '\033[93m'
RED_COLOR = '\033[31m'
END_COLOR = '\033[0m'


#this handles all the argument parsing for this script
def parse_args():
    parser = argparse.ArgumentParser(description="Use intel's PIN tool to enumerate flag length and flag")
    parser.add_argument("target", metavar='TARGET', type=str, help = "target executable that you expect to take the flag")
    charset_mutually_exclusive_group = parser.add_mutually_exclusive_group()
    charset_mutually_exclusive_group.add_argument('-w',action='store_true',help="use string.letters, string.digits, and string.whitespace as the charset")
    charset_mutually_exclusive_group.add_argument('-p',action='store_true',help="use string.printable as the charset")
    charset_mutually_exclusive_group.add_argument('-c', nargs=1, type=str, help="string containing your custom charset")
    parser.add_argument('-f',metavar="flag", nargs=1, type=str, help="a new flag starting point")
    parser.add_argument('-t', nargs=1, type=str, help="a character that you expect the flag to end with, DEFAULT = }")
    parser.add_argument('-P', nargs=1, type=str, help="the full path to your pin executable, NOTE, just the path without a terminating '/'")
    parser.add_argument('--enum',action='store_true',help="attempt to enumerate the flag length")
    parser.add_argument('--build',action='store_true',help="attempt to build flag")
    parser.add_argument('--build_length',action='store_true',help="attempt to build the flag with a set length")
    parser.add_argument('-l', nargs=1, type=str, help="the length of the flag, use with -build_length")
    parser.add_argument('-arch64',action='store_true',help="use a 64 bit version of the tool")
    parser.add_argument('-T', nargs=1, type=int, help="what tolerence to use between instruction counts for flag enumeration")
    args = parser.parse_args()
    try:
        global charset
        global target_executable
        global flag_builder
        global flag_terminator
        global pin_path
        global enumerate_flag
        global build_flag
        global tool_location
        global tool_path
        global tool_name
        global enumeration_tolerence
        global flag_length
        global build_flag_length
        target_executable = args.target
        if args.w:
            charset = WHITESPACE_CHARSET
        if args.p:
            charset = PRINTABLE_CHARSET
        if args.c:
            charset = args.c[0]
        if args.f:
            flag_builder = args.f[0]
        if args.t:
            flag_terminator = args.t[0]
        if args.P:
            pin_path = args.P[0]
            pin_location = pin_path + '/pin'
            tool_path = pin_path + '/source/tools/ManualExamples/obj-ia32'
            tool_name = 'inscount0.so'
            tool_location = tool_path+'/'+tool_name
        if args.l:
            flag_length = int(args.l[0])
        enumerate_flag = args.enum
        build_flag = args.build
        build_flag_length = args.build_length
        if args.arch64:
            tool_path = pin_path + '/source/tools/ManualExamples/obj-intel64' 
            tool_location = tool_path+'/'+tool_name
        if args.T:
            enumeration_tolerence = args.T[0]
            
    except Exception as e:
        parser.print_usage()
        print "args parsing error is %s ".format(e)

#this function is to print yellow text
def print_yellow(text):
    print YELLOW_COLOR + text + END_COLOR 

#this function is to print red text
def print_red(text):
    print RED_COLOR + text + END_COLOR


#this function will grab the instruction count that pin outputs and return as an int
def get_instruction_count():
    try:
        with open(inscount_filename,'r') as f:
            return int(f.read().strip().split(' ')[1])
    except Exception as e:
        print "unable to get instruction count, this usually means that the arguments to the pin tool were incorrect.  Is your architecture correct?"

#this function is for building a flag from a starting point.  Will not work if the program is checking for length
def build_flag_from_start():
    flag_temp = flag_builder
    print "targetting {} with flag {}".format(target_executable,flag_temp)
    while not flag_temp.endswith(flag_terminator):
        icounts_dict = {}
        print "trying:"
        for char in charset:
            sys.stdout.write(char)
            sys.stdout.flush()
            try:
                subprocess.check_output([pin_location, '-t', tool_location, '-o', 'inscount.log', '--', target_executable, flag_temp+char])
            except Exception as e:
                logging.debug(e)
                icounts_dict[get_instruction_count()] = char
        print ""
        if max(icounts_dict.keys(),key=int) == min(icounts_dict.keys(),key=int):
            print "all charaters in charset have same instruction count"
            print_yellow( "Flag to this point: {}".format(flag_temp))
            raise Exception("can't determine next character, you might have the Flag!")
        flag_temp += icounts_dict[max(icounts_dict.keys(),key=int)]
        print_yellow("known flag so far: {}".format(flag_temp))
    print_red("GOT FLAG: {}".format(flag_temp))

def enum_flag_length():
    flag_temp = flag_builder
    print "targetting {} with flag {}".format(target_executable,flag_temp)
    icounts_dict = {}
    while len(flag_temp) <= 50:
        print "trying length {}".format(str(len(flag_temp)))
        try:
            subprocess.check_output([pin_location, '-t', tool_location, '-o', 'inscount.log', '--', target_executable, flag_temp])
        except Exception as e:
            if e.returncode == 255:
                print "your pintool did not run correctly, does your user have permission to run /opt/pin/pin?  did you choose the correct architecture for binary you are targetting?"
                print e
            try:
                icounts_dict[get_instruction_count()] = flag_temp
            except Exception as e:
                logging.debug(e)
        if not (abs(max(icounts_dict.keys(),key=int) - min(icounts_dict.keys(),key=int)) < enumeration_tolerence) :
            print icounts_dict
            break
        flag_temp += 'z'
    if len(flag_temp) > 50:
        print_yellow("Unable to enumerate flag length")
    else:
        print_yellow("Got flag length: {}".format(str(len(icounts_dict[max(icounts_dict.keys(),key=int)]))))
        global flag_length 
        flag_length = len(icounts_dict[max(icounts_dict.keys(),key=int)])

#This function will attempt to build the flag when the flag must be a certain length to pass a length check.  length is the required length of the flag
def build_flag_with_length(length):
    flag_temp = flag_builder
    temp_len = len(flag_temp)
    target_char_index = temp_len
    flag_temp = flag_temp + DEFAULT_FILL_CHAR * (length-temp_len)
    print "targetting {} with flag {}".format(target_executable,flag_temp)
    while (not flag_temp.endswith(flag_terminator)) and  target_char_index < length:
        icounts_dict = {}
        print "trying:"
        for char in charset:
            sys.stdout.write(char)
            sys.stdout.flush()
            try:
                subprocess.check_output([pin_location, '-t', tool_location, '-o', 'inscount.log', '--', target_executable, flag_temp[:target_char_index]+char+flag_temp[target_char_index+1:]])
            except Exception as e:
                logging.debug(e)
                icounts_dict[get_instruction_count()] = flag_temp[:target_char_index]+char+flag_temp[target_char_index+1:]
        print ""
        if max(icounts_dict.keys(),key=int) == min(icounts_dict.keys(),key=int):
            print "all charaters in charset have same instruction count"
            print_yellow( "Flag to this point: {}".format(flag_temp))
            raise Exception("can't determine next character, you might have the Flag!")
        flag_temp = icounts_dict[max(icounts_dict.keys(),key=int)]
        target_char_index += 1
        print_yellow("known flag so far: {}".format(flag_temp))
    print_red("GOT FLAG: {}".format(flag_temp))
            

def main():
    parse_args()
    logging.basicConfig(format='%(levelname)s:%(message)s')
    if enumerate_flag:
        enum_flag_length()
    if build_flag:
        build_flag_from_start()

    if build_flag_length and flag_length == 0:
        raise "flag length must be set to use the build_length argument"
    elif build_flag_length and flag_length != 0:
        build_flag_with_length(flag_length)


if __name__ == "__main__":
    main()



