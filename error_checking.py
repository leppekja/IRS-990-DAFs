import read_990 as rd
import sys

def check_failures(failures_file):
    '''
    take in a txt file of failed to read files
    and return their form type and version
    Input: format objectid.xml \n
    output: [version, type] \n
    '''
    with open('Failures.txt') as f:
        with open('Fail_Analysis.txt', 'w') as g:
            for line in f:
                tree = rd.read_form('../990_forms/' + line.strip(), False) 
                checks = []
                checks.append(rd.get_form_version(tree))
                checks.append(rd.get_form_type(tree))
                g.write(str(checks) + '\n')


if __name__ == "__main__":
    check_failures(sys.argv[-1])