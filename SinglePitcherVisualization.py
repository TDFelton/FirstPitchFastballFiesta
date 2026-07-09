import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

Pitches = pd.read_csv("~/Downloads/Michigan/FirstPitchFastballFiesta/pitches_classified.csv")

# Filtering for a single player (ANI-9741 is good)
pitcher_id = "ANI-9741"
single_pitcher_df = Pitches[Pitches['pitcher'] == pitcher_id].copy()
single_pitcher_df = single_pitcher_df.sort_values("game_string")

# getting a new column for the sequence of games a pitcher appears in
unique_games = single_pitcher_df['game_string'].unique()
game_to_sequence = {game: f"Game {i+1}" for i, game in enumerate(unique_games)}
single_pitcher_df["game_sequence"] = single_pitcher_df["game_string"].map(game_to_sequence)

fig, ax = plt.subplots(figsize=(12, 6))

sns.stripplot(
    data=single_pitcher_df,
    x='game_sequence',
    y='velocity',
    hue='pitch_type',
    jitter=True,     
    size=6,
    alpha=0.8,
    palette={'Fastball': "#D7303E", 'Offspeed': "#1E385D", 'Unknown': "#8A9394"},
    ax=ax,
    dodge=False,
    edgecolor='k', linewidth=0.5
)

ax.set_title(f"Pitch Buckets by Game: {pitcher_id}", fontsize=14, pad=15)
ax.set_xlabel("Appearance", fontsize=10)
ax.set_ylabel("Velocity (MPH)", fontsize=12)

plt.xticks(rotation=45, ha='right')

ax.legend(title="Pitch Type", loc='best')
ax.grid(True, axis='y', linestyle=':', alpha=0.6)

plt.tight_layout()
plt.savefig('pitcher_games_bucketed.png', dpi=300)