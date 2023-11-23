import json
import os
from collections import defaultdict
import matplotlib.pyplot as plt
from datetime import datetime

# # Replace with your actual file paths
# file_paths = [
#     "/path/to/your/data/Streaming_History_Audio_2020_3.json",
#     "/path/to/your/data/Streaming_History_Audio_2020-2021_4.json",
#     "/path/to/your/data/Streaming_History_Audio_2021-2022_5.json",
# ]

# # Load data
# data = []
# for path in file_paths:
#     with open(path, "r") as file:
#         data.extend(json.load(file))


def load_data_from_directory(directory):
    data = []
    for filename in os.listdir(directory):
        if filename.endswith(".json"):
            filepath = os.path.join(directory, filename)
            with open(filepath, "r") as file:
                data.extend(json.load(file))
    return data


# Default directory where JSON files are located
default_data_directory = "./laura/"

# Load data from the default directory
data = load_data_from_directory(default_data_directory)


# Helper functions to generate plots
def plot_top_songs():
    songs_listen_count = defaultdict(int)

    for entry in data:
        artist_name = entry["master_metadata_album_artist_name"]
        song_name = entry["master_metadata_track_name"]
        combined_name = f"{artist_name} : {song_name}"
        songs_listen_count[combined_name] += 1

    top_10_songs = sorted(songs_listen_count.items(), key=lambda x: x[1], reverse=True)[
        :10
    ]

    song_artist_names = [item[0] for item in top_10_songs]
    listen_counts = [item[1] for item in top_10_songs]

    plt.figure(figsize=(12, 8))
    plt.barh(song_artist_names, listen_counts, color="skyblue")
    plt.xlabel("Listen Counts")
    plt.ylabel("Artist : Song")
    plt.title("Top 10 Songs of All Time")
    plt.gca().invert_yaxis()
    plt.tight_layout()

    # Save the plot to a file
    plt.savefig("static/top_songs_plot.png")
    plt.close()


def plot_monthly_listen_count():
    monthly_listen_count = defaultdict(int)

    for entry in data:
        timestamp_str = entry["ts"]
        timestamp = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%SZ")
        month_year = timestamp.strftime("%Y-%m")
        monthly_listen_count[month_year] += 1

    months = list(monthly_listen_count.keys())
    listen_counts = list(monthly_listen_count.values())

    plt.figure(figsize=(12, 8))
    plt.bar(months, listen_counts, color="lightblue")
    plt.xlabel("Month")
    plt.ylabel("Song Counts")
    plt.title("Number of Songs Listened to Each Month")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()

    # Save the plot to a file
    plt.savefig("static/monthly_listen_count_plot.png")
    plt.close()


plot_top_songs()
