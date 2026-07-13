# Import Packages
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import pyarrow.dataset as pads
import pyarrow.csv as pacsv
import sportypy
import sqlite3
from scipy.integrate import quad
from data.SMT_Data_Starter import readDataSubset

## Goals:
## 1. Grab start and end time of every pitch, tagged by pitcher. Include play ID and all relevant data.
##    --- find first pitch bool from lineups file
## 2. (later file) Use start and end time to tag ball positions throughout the pitch
## 3. Classify pitches by pitch type and find outcome (HR / barrel / not HR or barrel)

# Pulling ball events data, filtering to only PHD away team for smaller testing sample size
ball_events_subset = readDataSubset('ball-events',data_path="./data")
ball_events = ball_events_subset.to_table().to_pandas()
# print("Number of events: " + str(ball_events.size))
# ~160k events for PHD away team

# Filtering for events where ball is pitched
Pitches = ball_events[ball_events["ball_eventcode"] == 1]
Pitches = Pitches[["game_string", "play_per_game", "timestamp"]]
# start time = the timestamp at which the pitch is released
Pitches = Pitches.rename(columns={'timestamp':'pitch_release_time'})

# finding the end of every pitch: filter for contact, ball caught by catcher, or ball in dirt
# also include deflection (for HBP)
# AND previous play was a pitch
EndPitchEvents = ball_events[(((ball_events["ball_eventcode"] == 2) | (ball_events["ball_eventcode"] == 4)
                              | (ball_events["ball_eventcode"] == 9) | (ball_events["ball_eventcode"] == 16)))
                            & (ball_events["ball_eventcode"].shift(1) == 1)]
Pitches = pd.merge(Pitches, EndPitchEvents, on=["game_string", "play_per_game"], how = "left")
Pitches = Pitches.rename(columns={'timestamp':'pitch_end_time'})
Pitches["result_in_play"] = (Pitches["ball_eventcode"] == 4) # COULD BE FOUL
Pitches = Pitches[["game_string", "play_per_game", "pitch_release_time", "pitch_end_time", "result_in_play"]]
Pitches = Pitches.drop_duplicates()

# now incorporating the lineup data to get pitcher ID and first pitch data
lineups_subset = readDataSubset('lineups',data_path="./data")
lineups = lineups_subset.to_table().to_pandas()

Pitches = Pitches.merge(lineups[["game_string", "play_per_game", "pitcher", "batter"]],
              on=["game_string", "play_per_game"], how="left")

# creating previous event lookup table
lookup = lineups[["game_string", "play_per_game", "batter"]].copy()
lookup["play_per_game"] += 1
lookup = lookup.rename(columns={'batter':'prev_batter'})
Pitches = Pitches.merge(lookup[["game_string", "play_per_game", "prev_batter"]],
                        on=["game_string", "play_per_game"], how="left")

# finding first pitch based on batter == prev batter
Pitches["first_pitch"] = (Pitches["batter"] != Pitches["prev_batter"])
# not including prev batter but keeping batter in just in case
# will have to find ball in play data later anyway but whatever
Pitches = Pitches[["game_string", "play_per_game", "pitch_release_time", "pitch_end_time", "result_in_play", "first_pitch", "pitcher", "batter"]]

# filter for just first pitches
Pitches = Pitches[Pitches["first_pitch"] == True]
Pitches = Pitches.drop_duplicates(keep='first')
print(Pitches.head())
print(Pitches.size)

Pitches.to_csv("first_pitches.csv", index=False)