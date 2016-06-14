import subprocess, string, argparse, sys

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
enumeration_tolerence = 10
enumerate_flag = False
build_flag = False


WARNING_COLOR = '\033[93m'
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
    parser.add_argument('-e',action='store_true',help="attempt to enumerate the flag length")
    parser.add_argument('-b',action='store_true',help="attempt to build flag")
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
        if args.e:
            enumerate_flag = True
        if args.b:
            build_flag = True
        if args.arch64:
            tool_path = pin_path + '/source/tools/ManualExamples/obj-intel64' 
            tool_location = tool_path+'/'+tool_name
        if args.T:
            enumeration_tolerence = args.T[0]
            
    except Exception as e:
        parser.print_usage()
        print "args parsing error is %s ".format(e)

#this function is to print highlighted text
def print_warning(text):
    print WARNING_COLOR + text + END_COLOR 

#this function will grab the instruction count that pin outputs and return as an int
def get_instruction_count():
    with open(inscount_filename,'r') as f:
        return int(f.read().strip().split(' ')[1])

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
                #print e
                icounts_dict[get_instruction_count()] = char
        print ""
        if max(icounts_dict.keys(),key=int) == min(icounts_dict.keys(),key=int):
            print "all charaters in charset have same instruction count"
            print_warning( "Flag to this point: {}".format(flag_temp))
            raise Exception("can't determine next character")
        flag_temp += icounts_dict[max(icounts_dict.keys(),key=int)]
        print_warning("known flag so far: {}".format(flag_temp))
    print_warning("GOT FLAG: {}".format(flag_temp))

def enum_flag_length():
    flag_temp = flag_builder
    print "targetting {} with flag {}".format(target_executable,flag_temp)
    icounts_dict = {}
    while len(flag_temp) <= 50:
        print "trying length {}".format(str(len(flag_temp)))
        try:
            subprocess.check_output([pin_location, '-t', tool_location, '-o', 'inscount.log', '--', target_executable, flag_temp])
        except Exception as e:
            #print e
            icounts_dict[get_instruction_count()] = flag_temp
        flag_temp += 'z'
        if not abs(max(icounts_dict.keys(),key=int) - min(icounts_dict.keys(),key=int)) < enumeration_tolerence :
            break
            
    if len(flag_temp) > 50:
        print_warning("Unable to enumerate flag length")
    else:
        print_warning("Got flag length: {}".format(str(len(icounts_dict[max(icounts_dict.keys(),key=int)]))))
        global flag_length 
        flag_length = len(icounts_dict[max(icounts_dict.keys(),key=int)])
        
 

def main():
    if enumerate_flag:
        enum_flag_length()
    if build_flag:
        build_flag_from_start()


if __name__ == "__main__":
    parse_args()
    main()



