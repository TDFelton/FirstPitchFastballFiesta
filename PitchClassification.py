import pandas as pd
import pyarrow.dataset as pads
import os
import polars as pl
from sympy import group
from SMT_Data_Starter import readDataSubset

#Reading in the data subsets using ReadDataSubset function from SMT_Data_Starter.py
ball_position_subset = readDataSubset('ball-positions',data_path="/Users/charlesmerkel/Desktop/SMT_Project/SMT-Data-Challenge-2026")
ball_position = ball_position_subset.to_table().to_pandas()
ball_events_subset = readDataSubset('ball-events',data_path="/Users/charlesmerkel/Desktop/SMT_Project/SMT-Data-Challenge-2026")
ball_events = ball_events_subset.to_table().to_pandas()


#Building a pitch summary table for grouped by game and play
#Pairs Represent cutoffs for the start and end of a pitch
summary_table = []
start_pair = (1,1)
terminal_pairs = {(2,2),(10,4),(2,7),(2,9),(255,16)}

grouped_keys = ball_events.groupby(['game_string', 'play_per_game'])

'''for (game, play),event in grouped_keys:
    event = event.sort_values("timestamp")
    print(game,play)
    print(event[[
        "timestamp",
        "player_id",
        "ball_eventcode"
    ]]) '''

for (game, play), event in grouped_keys:
    event = event.sort_values("timestamp").reset_index(drop=True)
    start_idx = None
    start_time = None
    end_time = None
    outcome = None

    for i, row in event.iterrows():
        if (row["player_id"], row["ball_eventcode"]) == start_pair:
            start_idx = i
            start_time = row["timestamp"]
            break
    if start_idx is None:
        #print(f"No pitch found for {game}, play {play}")
        continue
    #print(f"\nGame: {game}, Play: {play}")
    #print("Looking for:", terminal_pairs)
    #print(f"start_idx = {start_idx}")
    #print(f"len(event) = {len(event)}")

    for i in range(start_idx + 1, len(event)):
        #print("Entered second loop")
        row = event.iloc[i]
        #print("Checking:", (row["player_id"], row["ball_eventcode"]))
        if (row["player_id"], row["ball_eventcode"]) in terminal_pairs:
            #print("MATCH!")
            end_time = row["timestamp"]
            outcome = row["ball_eventcode"]
            break
    
    summary_table.append({
        "game_string": game,
        "play_per_game": play,
        "start_time": start_time,
        "end_time": end_time,
        "outcome": outcome
    })

print(summary_table[:10])