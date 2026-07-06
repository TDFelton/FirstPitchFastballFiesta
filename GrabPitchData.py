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

# Pulling ball events data, filtering to only VAS away team for smaller testing sample size
ball_events_subset = readDataSubset('ball-events',data_path="/Users/adrianveto/Downloads/Michigan/FirstPitchFastballFiesta/data")
ball_events = ball_events_subset.to_table(filter = (pads.field('home_team') == "VAS")).to_pandas()
# print("Number of events: " + str(ball_events.size))
# ~160k events for VAS away team

# Filtering for events where ball is pitched
Pitches = ball_events[ball_events["ball_eventcode"] == 1]
Pitches = Pitches[["game_string", "play_per_game", "timestamp"]]
# start time = the timestamp at which the pitch is released
Pitches = Pitches.rename(columns={'timestamp':'pitch_release_time'})

# finding the end of every pitch: filter for contact, ball caught by catcher, or ball in dirt
# also include deflection (for HBP)
# AND previous play was a pitch
EndPitchEvents = ball_events[((ball_events["ball_eventcode"] == 2) | (ball_events["ball_eventcode"] == 4)
                              | (ball_events["ball_eventcode"] == 9) | (ball_events["ball_eventcode"] == 16))
                            & ball_events["ball_eventcode"].shift(1) == 1]
Pitches = pd.merge(Pitches, EndPitchEvents, on=["game_string", "play_per_game"], how = "left")
Pitches = Pitches.rename(columns={'timestamp':'pitch_end_time'})
Pitches["result_in_play"] = (Pitches["ball_eventcode"] == 4) # COULD BE FOUL
Pitches = Pitches[["game_string", "play_per_game", "pitch_release_time", "pitch_end_time", "result_in_play"]]

# now incorporating the lineup data to get pitcher ID and first pitch data
lineups_subset = readDataSubset('lineups',data_path="/Users/adrianveto/Downloads/Michigan/FirstPitchFastballFiesta/data")
lineups = lineups_subset.to_table(filter = (pads.field('home_team') == "VAS")).to_pandas()

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


# merge HR events so we can tell if ball in play is a HR
# will function similarly once we have barrel dataframe
HREvents = ball_events[(ball_events["ball_eventcode"] == 11)]
Pitches = pd.merge(Pitches, HREvents, on=["game_string", "play_per_game"], how = "left")
Pitches["result_HR"] = (Pitches["ball_eventcode"] == 11)
Pitches = Pitches[["game_string", "play_per_game", "pitch_release_time", "pitch_end_time", "first_pitch", "pitcher", "batter", "result_in_play", "result_HR"]]
# print(Pitches.head())


# finding the points of each pitch
# goal: get the first point, second point, and final point of each pitch (and their timestamps)
# use the first two points to trace a line (incl. gravity) to home plate for break
# calculate velocity from first and final point and delta_y

ball_positions_subset = readDataSubset('ball-positions',data_path="/Users/adrianveto/Downloads/Michigan/FirstPitchFastballFiesta/data")
ball_positions = ball_positions_subset.to_table(filter = (pads.field('home_team') == "VAS")).to_pandas()

# create a temporary df to get ALL ball positions with game string and PPG
temp_df = pd.merge(ball_positions[["game_string", "play_per_game", "timestamp", "ball_position_x", "ball_position_y", "ball_position_z"]], 
                   Pitches[["game_string", "play_per_game", "pitch_release_time", "pitch_end_time"]],
                   on=["game_string", "play_per_game"])
# filtering out plays outside the pitch time
temp_df = temp_df[(temp_df["timestamp"] >= temp_df["pitch_release_time"]) &
                  (temp_df["timestamp"] <= temp_df["pitch_end_time"])]
# making sure everything is chronological so grabbing by index works
temp_df = temp_df.sort_values(by=["game_string", "play_per_game", "timestamp"])

# grouping by game and PPG
grouped = temp_df.groupby(["game_string", "play_per_game"])
first_pos = grouped.nth(0).reset_index()
second_pos = grouped.nth(1).reset_index()
final_pos = grouped.nth(-1).reset_index()

# must rename columns
first_pos = first_pos.rename(columns={"timestamp":"first_timestamp", "ball_position_x":"first_ball_position_x", "ball_position_y":"first_ball_position_y", "ball_position_z":"first_ball_position_z"})
second_pos = second_pos.rename(columns={"timestamp":"second_timestamp", "ball_position_x":"second_ball_position_x", "ball_position_y":"second_ball_position_y", "ball_position_z":"second_ball_position_z"})
final_pos = final_pos.rename(columns={"timestamp":"final_timestamp", "ball_position_x":"final_ball_position_x", "ball_position_y":"final_ball_position_y", "ball_position_z":"final_ball_position_z"})

PitchPositions = Pitches.merge(first_pos, on=["game_string", "play_per_game"], how="left")
PitchPositions = PitchPositions.merge(second_pos, on=["game_string", "play_per_game"], how="left")
PitchPositions = PitchPositions.merge(final_pos, on=["game_string", "play_per_game"], how="left", suffixes=("_left", "_right"))
PitchPositions = PitchPositions.drop(columns=["pitch_release_time_y", "pitch_end_time_y", "pitch_release_time_left",
                             "pitch_end_time_left", "pitch_release_time_right", "pitch_end_time_right", "index", "index_y", "index_x"])
PitchPositions = PitchPositions.drop(columns=["pitch_release_time", "pitch_end_time"])
# print(PitchPositions.head())

# Now that we have the positions, we want to project through the first two points to find an expected endpoint at the final x and z
PitchPositions["delta_y"] = PitchPositions["first_ball_position_y"] - PitchPositions["final_ball_position_y"] # in feet
PitchPositions["time"] = PitchPositions["final_timestamp"] - PitchPositions["first_timestamp"] # in ms
PitchPositions["velocity"] = round((PitchPositions["delta_y"] / PitchPositions["time"]) * 681.818, 2)  ## to convert ft/ms -> mph

# PitchPositions["partial_time"] = PitchPositions["second_timestamp"] - PitchPositions["first_timestamp"]
# PitchPositions["velo_x"] = (PitchPositions["first_ball_position_x"] - PitchPositions["second_ball_position_x"]) / PitchPositions["partial_time"]
# PitchPositions["velo_z"] = (PitchPositions["first_ball_position_z"] - PitchPositions["second_ball_position_z"]) / PitchPositions["partial_time"]

# PitchPositions["projected_x"] = PitchPositions["first_ball_position_x"] + (PitchPositions["velo_x"] * PitchPositions["time"])
# # MLB projected z uses gravity as well. Faster version of ours skips the integral -> more break on everything
# # PitchPositions["projected_z"] = PitchPositions["first_ball_position_z"] + (PitchPositions["velo_z"] * PitchPositions["time"])
# PitchPositions["projected_z"] = PitchPositions["first_ball_position_z"] + (PitchPositions["velo_z"] * PitchPositions["time"]) - (4.905 * ((PitchPositions["time"] / 1000) ** 2))

# PitchPositions["horizontal_break"] = PitchPositions["final_ball_position_x"] - PitchPositions["projected_x"]
# PitchPositions["vertical_break"] = PitchPositions["final_ball_position_z"] - PitchPositions["projected_z"]

# PitchPositions = PitchPositions.drop(columns=["delta_y", "time", "partial_time", "velo_x", "velo_z", "projected_x", "projected_z"])
PitchPositions = PitchPositions.drop(columns=["delta_y", "time"])
PitchPositions = PitchPositions.drop(columns=["first_timestamp", "first_ball_position_x", "first_ball_position_y", "first_ball_position_z",
                                              "second_timestamp", "second_ball_position_x", "second_ball_position_y", "second_ball_position_z",
                                              "final_timestamp", "final_ball_position_x", "final_ball_position_y", "final_ball_position_z"])
print(PitchPositions.head())

PitchPositions.to_csv("VAS_pitches.csv", index=False)
