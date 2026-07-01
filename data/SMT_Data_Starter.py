import pandas as pd
import pyarrow.dataset as pads
import os
import polars as pl

"""
Welcome to the SMT Data Challenge! Here is a function to help you get
started. Ensure that Pandas and Pyarrow, and os are installed before proceeding. 
The functions included below define Pyarrow datasets that can be referenced 
elsewhere in your code for the purposes of querying data. 

Calling this function on a data subtype only creates a dataset, not a table or 
DataFrame. Instead, you should call something like this to convert the dataset
to a Pandas DataFrame:

    dataset.to_table().to_pandas()
    
Other examples of filter and select statements are included in the main function
below.

WARNING: The data subsets are large, especially `player-positions`. Reading the 
  entire subset at once without filtering may incur performance issues on your 
  machine or even crash your session. It is recommended that you include filters 
  when you query the datasets before saving them into the working environment. 
  See https://arrow.apache.org/docs/python/dataset.html#filtering-data for info 
  on how to filter Arrow datasets before bringing them into memory.
"""

# For the data_path argument, include the full file path to the folder that holds the data!    
def readDataSubset(table_type, data_path="C:\\Users\\b.fryer\\Desktop\\SMT-Data-Challenge-2026"):
    '''
    Takes a the set of tables from Data set and
    transforms into panda data frame for manipulation
    
    Input:
    -     table_type   = Set of tables of interest from Data set [str]
    -     data_path    = File Path which data is located in Local device, change as necessary[str]
    
    '''
    if table_type not in ['ball-positions', 'ball-events', 'player-positions', 'lineups', 'game-info']:
        print("Invalid data subset name. Please try again with a valid data subset.")
        return -1

    if table_type == 'lineups' or table_type == 'game-info':
        return pads.dataset(source = os.path.join(os.path.dirname(__name__), data_path, table_type + '.csv'), format = 'csv')
    else:
        return pads.dataset(source = os.path.join(os.path.dirname(__name__), data_path, table_type), format = 'csv', partitioning = ['home_team', 'away_team', 'year', 'day'])

def main():
    # Read data subsest
    player_pos_df = readDataSubset('ball-events')

    # Define criteria to filter data subset on
    # You may pass this directly to the `filter` argument of `to_table()` if you choose
    filter_criteria = (pads.field('game_string') == "y1_d061_VKA_PHD")

    # Apply your row filters and column projection in the `to_table()` function,
    # then convert to Pandas DataFrame with `to_pandas()`
    filtered_df = player_pos_df.to_table(filter=filter_criteria).to_pandas()

    # To convert the data to a polars data frame, use `pl.from_pandas`
    final_df = pl.from_pandas(filtered_df)


    print(final_df)

if __name__ == "__main__":
    main()