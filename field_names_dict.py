import pandas as pd
import sys

def writer(file):
    '''
    Get field names of CSV file and print to new
    text file to review. 
    '''
    data = pd.read_csv(file, nrows=1)
    b = [i.upper() for i in data.columns] 
    with open(file[:-4] + '_fields.txt', 'w') as f:
        f.write('\n'.join(b)) 

    return None

if __name__ == '__main__':
    writer(sys.argv[-1])