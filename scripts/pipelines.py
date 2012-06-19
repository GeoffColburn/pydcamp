#!/usr/bin/env python
import argparse
import os, sys

class common:
    @staticmethod
    def gbk2fasta(gbk, fasta):
        out = open(fasta, 'w')
        found_origin = False
        for line in open(gbk, 'r'):
            if line.startswith("LOCUS"):
                out.write('>' + line.split()[1] + '\n')
            elif line.startswith("ORIGIN"):
                found_origin = True
            elif found_origin:
                tokens = line.split()
                seq = "".join(tokens[1:]).upper()
                out.write(seq + '\n')
        common.assert_file(fasta)

    @staticmethod
    def assert_file(path, cmd = None):
        if not os.path.exists(path) or os.path.getsize(path) == 0:
            print >> sys.stderr, "###ERROR"
            print >> sys.stderr, "File not created: ", path
            if not cmd == None:
                print >> sys.stderr, "From command: ", cmd
            print >> sys.stderr, "###"
            sys.exit(-1)
    
        return
        

    @staticmethod
    def system(cmd):
        print >> sys.stderr, cmd
        return os.system(cmd)

    @staticmethod
    def new_file_path(file_path, new_dir):
        return os.path.join(new_dir, os.path.basename(file_path))

    @staticmethod
    def merge_files(file_name_1, file_name_2):
        file1 = open(file_name_1, 'a')
        file2 = open(file_name_2, 'r')
        
        for line in file2.readlines():
            file1.write(line)
        
        file1.close()
        file2.close()


                

def do_gbk2fasta(args):
    common.gbk2fasta(args.gbk, args.fasta)
    return

def do_bowtie(args):
    if not os.path.exists(args.output): os.makedirs(args.output)

    gbk_path = args.ref_paths[0]
    fasta_path = os.path.join(args.output, "reference.fasta")
    common.gbk2fasta(gbk_path, fasta_path)

    prefix = fasta_path.replace(".fasta", "")
    cmd = "bowtie-build {} {}".format(fasta_path, prefix)
    common.system(cmd)

    sam_path = os.path.join(args.output, "reference.sam")
    cmd = "bowtie -S {} {} {}".format(prefix, ",".join(args.read_paths), sam_path) 
    common.system(cmd)
    common.assert_file(sam_path, cmd)

    print "Bowtie Created: ",  sam_path


    return fasta_path, sam_path



    

def main():
    main_parser = argparse.ArgumentParser()
    subparser = main_parser.add_subparsers()

    #gbk2fasta
    gbk2fasta_parser = subparser.add_parser("gbk2fasta")
    gbk2fasta_parser.add_argument("--gbk", dest = "gbk", required = True)
    gbk2fasta_parser.add_argument("--fasta", dest = "fasta", required = True)
    gbk2fasta_parser.set_defaults(func = do_gbk2fasta)

    #bowtie.
    bowtie_parser = subparser.add_parser("bowtie")
    bowtie_parser.add_argument("-o", dest = "output", required = True)
    bowtie_parser.add_argument("-r", action = "append", dest = "ref_paths", required = True)
    bowtie_parser.add_argument("--paired-ends", action = "store_true", dest = "pair_ended", default = False)
    bowtie_parser.add_argument("read_paths", nargs = '+')
    bowtie_parser.set_defaults(func = do_bowtie)


    args = main_parser.parse_args()
    args.func(args)



if __name__ == '__main__':
   main() 
