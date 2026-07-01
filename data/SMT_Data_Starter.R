#' Welcome to the SMT Data Challenge! Here are some functions to help you get
#' started. After you unzip the dataset, copy the name of the directory you saved 
#' it to into the 'data_directory` field below. After making sure you have the 
#' `arrow` package installed, you may call this file at the top of your work file(s)
#' by calling `source("SMT_Data_starter.R"). Then, you may apply functions and 
#' operations to the table names below as you would any other table and load them 
#' into your working environment by calling `collect()`. For an example of this 
#' process, un-comment and run the lines below the starter code. 
#'  
#' WARNING: The data subsets are large, especially `player-positions`. Reading the 
#'   entire subset at once without filtering may incur performance issues on your 
#'   machine or even crash your R session. It is recommended that you filter 
#'   data subsets wisely before calling `collect()`.

# Include the full file path to the folder that holds the data here!
data_directory <- "C:/Users/b.fryer/Desktop/Organizer-SMT-Data-Challenge-2026"

# Load Data - DO NOT MODIFY ----

if(!require("arrow")) {install.packages("arrow")}; library(arrow)
if(!require("tidyverse")) {install.packages("tidyverse")}; library(tidyverse)
if(!require("sportyR")) {install.packages("sportyR")}; library(sportyR)
if(!require("gganimate")) {install.packages("gganimate")}; library(gganimate)

ball_positions <- arrow::open_csv_dataset(paste0(data_directory,"/ball-positions"), 
                                    partitioning = c("home_team", "away_team", "year", "day"), 
                                    col_names = c("game_string", "play_per_game", "timestamp",
                                                 "ball_position_x", "ball_position_y", "ball_position_z"),
                                    hive_style = F, 
                                    unify_schemas = T, 
                                    na = c("", "NA", "NULL", NA, "\\N"))

ball_events <- arrow::open_csv_dataset(paste0(data_directory,"/ball-events"), 
                                       partitioning = c("home_team", "away_team", "year", "day"),  
                                       hive_style = F, 
                                       unify_schemas = T, 
                                       na = c("", "NA", "NULL", NA, "\\N"))

player_positions <- arrow::open_csv_dataset(paste0(data_directory,"/player-positions"), 
                                      partitioning = c("home_team", "away_team", "year", "day"), 
                                      col_names = c("game_string", "play_per_game", "timestamp",
                                                   "player_id", "field_x", "field_y"),
                                      hive_style = F, 
                                      unify_schemas = T, 
                                      na = c("", "NA", "NULL", NA, "\\N"))

lineups <- arrow::open_csv_dataset(paste0(data_directory,"/lineups.csv"), 
                                   hive_style = F, 
                                   unify_schemas = T, 
                                   na = c("", "NA", "NULL", NA, "\\N")) %>% 
  collect()

game_info <- arrow::open_csv_dataset(paste0(data_directory,"/game-info.csv"), 
                                     hive_style = F, 
                                     unify_schemas = T, 
                                     na = c("", "NA", "NULL", NA, "\\N")) %>% 
  collect()

# Play Animation Function ----

animate_play <- function(game_string_input = "y1_d061_VKA_PHD",
                         play_per_game_input = 8) {
  
  # Set the specs for the gif we want to create (lower res to make it run quicker)
  options(gganimate.dev_args = list(width = 3, height = 3, units = 'in', res = 120))
  
  #' #ometimes the frames per second at different stadiums can vary (30 fps vs 50 fps)
  #' this finds an even rounding interval and calculates fps from the data explicitly
  fps <- player_positions %>%
    # Filter to Correct Game
    filter(game_string == game_string_input & 
             play_per_game == play_per_game_input) %>%
    # Collect from Arrow
    collect() %>%
    # Double check columns are numeric
    mutate(across(c(timestamp, field_x, field_y, player_id),
                  as.numeric)) %>%
    # Filter for only Players
    filter(player_id < 14) %>%
    # Calculate Frames Per Second by player's position
    mutate(fps = timestamp - lag(timestamp), 
           .by = "player_id")  %>%
    # Calculate Frames Per Second and save as a vector
    count(fps) %>% slice_max(n) %>% pull(fps)
  
  # Find the time of the pitch
  time_of_pitch <-  ball_events %>%
    filter(game_string == game_string_input &
             play_per_game == play_per_game_input &
             ball_eventcode == 1) %>%
    collect() %>%
    pull(timestamp)
  
  # Get the Ball Tracking Data
  ball_tracking_data <- ball_positions %>%
    ## Filter to correct game
    filter(game_string == game_string_input &
             play_per_game == play_per_game_input) %>%
    ## Collect from Arrow
    collect() %>%
    ## Add on a type and player_id column to match with player_tracking_data
    mutate(type = "ball", 
           player_id = NA) %>% 
    ## Reorder and Rename Columns
    select(game_string:timestamp, player_id, type, position_x = ball_position_x,
           position_y = ball_position_y, position_z = ball_position_z, everything())
  
  # Get the Player Tracking Data
  player_tracking_data <- player_positions %>%
    ## Filter to the Correct Game
    filter(game_string == game_string_input &
             play_per_game == play_per_game_input) %>%
    ## Collect from Arrow
    collect() %>%
    ## Convert player_id to numeric
    mutate(player_id = as.numeric(player_id)) %>%
    ## Calculate type and put position_z as NA
    mutate(type = case_when(player_id <= 9 ~ "defense",
                            between(player_id, 10, 13) ~ "offense",
                            between(player_id, 14, 17) ~ "umpire",
                            player_id %in% c(18, 19) ~ "coach"),
           position_z = NA
    ) %>%
    ## Reorder and Rename Columns
    select(game_string:timestamp, player_id, type, position_x = field_x,
           position_y = field_y, position_z, everything())
  
  # Combine all tracking data into 1 data frame
  tracking_data <- bind_rows(player_tracking_data, ball_tracking_data) %>% 
    ## Convert timestamps and positions to numeric
    mutate(across(c(timestamp, position_x, position_y, position_z), 
                  as.numeric)) %>%
    ## Order data chronologically
    arrange(timestamp) %>%
    ## Align timestamps to account for mechanical measurement error
    mutate(timestamp_adj = plyr::round_any(timestamp, fps)) %>%
    ## Start the animation to start when the pitch is thrown
    filter(timestamp >= time_of_pitch) %>%
    ## Create a frame_id for animation
    mutate(frame_id = match(timestamp_adj, unique(timestamp_adj)))
  
  # Make Field and Plot Points
  p <- geom_baseball(league = "MiLB") +
    ## Plot all people as dots
    geom_point(data = tracking_data %>% filter(type != "ball"),
               aes(x = position_x, y = position_y, fill = type),
               shape = 21, size = 3,
               show.legend = F) +
    ## Label on top of the people dots 
    geom_text(data = tracking_data %>% filter(type == "defense"),
              aes(x = position_x, y = position_y, label = player_id),
              color = "black", size = 2,
              show.legend = F) +
    ## Plot the ball
    geom_point(data = tracking_data %>%
                 filter(type == "ball"),
               aes(x = position_x, y = position_y,
                   size = position_z),
               fill = "white",
               shape = 21,
               show.legend = F) +
    ## Specify colors for people
    scale_fill_manual(values = c("offense" = "#005AB5",
                                 "defense" = "#FEFE62",
                                 "coach" = "#1A85FF",
                                 "umpire" = "black")) +
    ## Specify when to transition
    transition_time(frame_id) +
    ## Annotate with the Play and Game ID
    annotate("text", x = c(150, 0), y = c(10, 400), color = "white",
             label = c(paste("Play:", play_per_game_input), paste("Game :", game_string_input))) +
    ## Add Shadows
    shadow_wake(0.1, exclude_layer = c(1:16))
  
  # Find the number of frames
  number_of_frames <-  max(tracking_data$frame_id)
  
  # Animate
  p2 <- animate(p, fps = fps, nframes = number_of_frames)
  
  return(p2)
}

# Play by Play Function ----

create_play_by_play <- function(game_string_input = "y1_d061_VKA_PHD",
                                play_per_game_input = 8) {
  
  # Internal Helper Function for converting player IDs to baseball positions
  player_position_definition <- function(code) {
    switch (as.character(code),
            "0" = "none",
            "1" = "pitcher",
            "2" = "catcher",
            "3" = "first baseman",
            "4" = "second baseman",
            "5" = "third baseman",
            "6" = "shortstop",
            "7" = "left fielder",
            "8" = "center fielder",
            "9" = "right fielder",
            "10"= "batter",
            "11" = "runner on first base",
            "12" = "runner on second base",
            "13" = "runner on third base",
            "14" = "home plate umpire",
            "15" = "field umpire",
            "16" = "field umpire",
            "17" = "field umpire",
            "18" = "first base coach",
            "19" = "third base coach",
            "255" = "ball event with no player"
    )
  }
  
  # Internal Helper Function for converting ball_eventcodes to events by name
  game_events_definition <- function(code) {
    
    switch (as.character(code),
            "1" = "pitch thrown",
            "2" = "ball acquired",
            "3" = "throw (ball-in-play)",
            "4" = "ball hit into play",
            "5" = "end of play.",
            "6" = "pickoff throw",
            "7" = "ball acquired - unknown field position",
            "8" = "throw (ball-in-play) - unknown field position",
            "9" = "ball deflection",
            "10"= "ball deflection off of wall",
            "11" = "home run",
            "16" = "ball bounce"
    )
  }
  
  ball_events %>%
    ## Filter to proper game and play
    filter(game_string == game_string_input &
             play_per_game_input == play_per_game) %>%
    ## Select Necessary Columns
    select(ball_eventcode, player_id) %>%
    ## Collect from Arrow
    collect() %>% 
    # Convert to text
    mutate(event = map_chr(ball_eventcode, game_events_definition),
           player = map_chr(player_id, player_position_definition),
           pbp = case_when(
             player != "none" & ball_eventcode != 16 ~ paste(event, "by", player),
             .default = event)) %>% 
    # Pull the pbp column and make it readable
    pull(pbp) %>% str_flatten_comma() %>% str_to_sentence()
}
