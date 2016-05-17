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


#this handles all the argument parsing for this script
def parse_args():
    parser = argparse.ArgumentParser(description="Use intel's PIN tool to enumerate flag length and flag")
    parser.add_argument("target", metavar='TARGET', type=str, help = "target executable that you expect to take the flag")
    charset_mutually_exclusive_group = parser.add_mutually_exclusive_group()
    charset_mutually_exclusive_group.add_argument('-w',action='store_true',help="use string.letters, string.digits, and string.whitespace as the charset")
    charset_mutually_exclusive_group.add_argument('-p',action='store_true',help="use string.printable as the charset")
    parser.add_argument("-f",metavar="flag", nargs=1, type=str, help="a new flag starting point")
    #add terminator and add pin location and 
    args = parser.parse_args()
    try:
        global charset
        global target_executable
        global flag_builder
        target_executable = args.target
        if args.w:
            charset = WHITESPACE_CHARSET
        elif args.p:
            charset = PRINTABLE_CHARSET
        elif args.f:
            flag_builder = args.f
    except Exception as e:
        parser.print_usage()
        print "args parsing error is ",e

#this function will grab the instruction count that pin outputs and return as an int
def get_instruction_count():
    with open(inscount_filename,'r') as f:
        return int(f.read().strip().split(' ')[1])

#this function is for building a flag from a starting point.  Will not work if the program is checking for length
def build_flag_from_start():
    print "targetting " + target_executable
    
    flag_temp = flag_builder
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
        flag_temp += icounts_dict[max(icounts_dict.keys(),key=int)]
        print "known flag so far: {}".format(flag_temp)
    print "GOT FLAG: {}".format(flag_temp)

def main():
    build_flag_from_start()


if __name__ == "__main__":
    parse_args()
    main()


