import sys

def arg_parser(arg_name, value=False, required=False, default=False):
    if arg_name in sys.argv:
        if not value:
            return True
        else:
            index = sys.argv.index(arg_name)
            if len(sys.argv) > index+1:
                return sys.argv[index+1].decode("utf-8")
            elif required:
                print "Missing value after parameter "+arg_name
                sys.exit()
    elif required:
        print "Missing parameter "+arg_name
        sys.exit()
    
    return default
