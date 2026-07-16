import pandas as pd
from sklearn.cluster import KMeans
import numpy as np
import matplotlib.pyplot as plt

Pitches = pd.read_csv("./pitches.csv")
print(len(Pitches))

# Goal: Use K-means clustering to get fastballs and non-fastballs from our existing DF
# Function to classify pitches. We'll apply this function to every pitcher in our DF
def classify_pitches(pitches_group):
    # dropping NA velocities
    CleanPitches = pitches_group.dropna(subset=["velocity"])

    # not enough data to classify
    if len(CleanPitches) < 5:
        pitches_group["pitch_type"] = "Unknown"
        return pitches_group
    
    # Now going to fit K-means
    # using two groups: fastball and non-fastball
    X = CleanPitches["velocity"].values.reshape(-1,1)
    kmeans = KMeans(n_clusters=2, random_state=1, n_init=10).fit(X)

    # the fastballs are the group with the higher avg velo
    fastball_cluster = np.argmax(kmeans.cluster_centers_)

    # now adding fastball or non fastball to data
    pitches_group["pitch_type"] = "Unknown" # default for NA values
    labels = np.where(kmeans.labels_ == fastball_cluster, "Fastball", "Offspeed")
    pitches_group.loc[CleanPitches.index, "pitch_type"] = labels

    return pitches_group


# now applying the clustering to each pitcher individually
Pitches = Pitches.groupby("pitcher", group_keys=False).apply(classify_pitches)
print(Pitches.head())

Pitches.to_csv("pitches_classified.csv", index=False)