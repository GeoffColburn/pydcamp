#!/usr/bin/env python
import sys, os
import argparse
import glob
import libdcamp.common as common

def do_errors(args):
    """Compare the existence of output.gd files with that of *.log.txt, if there is not an
    output.gd for for a log file then it must have failed and needs to be brought to the
    users attention."""
    test_search = os.path.join(args.test_dir, "*/output/output.gd")
    log_search = os.path.join(args.log_dir,"*.log.txt")

    print >> sys.stderr, "GenomeDiff search:", test_search
    print >> sys.stderr, "Log search:", log_search

    test_paths = glob.glob(test_search)
    test_paths = (path.replace("/output/output.gd", "") for path in test_paths)
    test_paths = map(os.path.basename, test_paths)
    test_names = set(test_paths)
    
    log_paths = glob.glob(log_search)
    log_paths = map(os.path.basename, log_paths)
    log_paths = (path.replace(".log.txt", "") for path in log_paths)
    log_names = set(log_paths)

    error_names = log_names.difference(test_names)

    if not len(error_names):
        print >> sys.stderr, "No errors!"
        return 0

    error_paths = [os.path.join(args.log_dir, name) + ".log.txt" for name in error_names]

    for path in error_paths:
        print 20 * '*'
        common.system("tail " + path)
        print 20 * '*'
        print

    return -1
    


def main():
    main_parser = argparse.ArgumentParser()
    subparser    = main_parser.add_subparsers()

    error_parser = subparser.add_parser("errors")
    error_parser.add_argument("-t", dest = "test_dir", default = "03_Output") 
    error_parser.add_argument("-l", dest = "log_dir", default = "04_Logs")
    error_parser.set_defaults(func = do_errors)


    args = main_parser.parse_args()
    args.func(args)



if __name__ == "__main__":
    main()
