
import sys

import regularExpressions
import xPath
import roadRunner

def main():
    printing = True
    
    arguments = sys.argv
    method = arguments[1]
    
    if(method == 'A'):
        regularExpressions.main(printing)
    elif(method == 'B'):
        xPath.main(printing)
    elif(method == 'C'):
        roadRunner.main(printing)

if __name__ == "__main__":
    main()