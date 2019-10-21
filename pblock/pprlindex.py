import gzip
import math
import random
from tqdm import tqdm
from itertools import product
import time


class PPRLIndex:
    """General class that implements an indexing technique for PPRL."""

    def __init__(self, nparty):
        """Initialise base class.

        Parameters
        ----------
        nparty: int
            Number of parties

        """
        self.nparty = nparty
        self.rec_dict = {}
        self.ent_id_cols = {}
        self.rec_id_cols = {}


    def __read_csv_file__(self, file_name, header_line, rec_id_col=None):
        """This method reads a comma separated file and returns a dictionary where
           the keys are the unique record identifiers (either taken from the file
           or assigned by the function) and the values are lists that contain the
           actual records.

           Arguments:
           - file_name    The name of the CSV file to read. If the file ends with
                          a '.gz' extension it is assumed it is GZipped.
           - header_line  A flag, True or False, if True then the first line is
                          assumed to contain the column (attribute) names and it
                          is skipped.
           - rec_id_col   The number (starting from 0) of the column that contains
                          unique record identifiers. If no such are available in
                          the file then this value must be set to None (default).
                          In this case each record is given a unique integer
                          number as identifier.
        """
        assert header_line in [True,False]

        rec_dict = {}  # Dictionary to contain the read records

        if (file_name.lower().endswith('.gz')):
          in_file =  gzip.open(file_name)  # Open gzipped file
        else:
          in_file =  open(file_name)  # Open normal file

        # Skip header line if necessary
        #
        if (header_line == True):
          header_line = in_file.readline()  # Skip over header line

        rec_count = 0

        for rec in in_file:
          rec = rec.lower().strip()
          if type(rec) == bytes:
            rec = rec.decode()
          rec = rec.split(',')
          clean_rec = list(map(lambda x: x.strip(), rec))  # Remove all surrounding whitespaces

          if (rec_id_col == None):
            rec_id = str(rec_count)  # Assign unique number as record identifier
          else:
            rec_id = clean_rec[rec_id_col]  # Get record identifier from file

          assert rec_id not in rec_dict, ('Record ID not unique:', rec_id)

          rec_dict[rec_id] = clean_rec

          rec_count += 1
        #print rec_dict
        return rec_dict
