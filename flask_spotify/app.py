from flask import Flask, render_template, request, redirect, url_for
import json
import os
from collections import defaultdict
import matplotlib.pyplot as plt
from datetime import datetime

app = Flask(__name__)

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


# Helper function
# Modify the plot_top_songs function to accept exclude_artist_list
def plot_top_songs(num_top_songs=10, exclude_artist_list=None):
    if not (1 <= num_top_songs <= 50):
        raise ValueError("Number of top songs must be between 1 and 50.")

    songs_listen_count = defaultdict(int)

    for entry in data:
        artist_name = entry["master_metadata_album_artist_name"]
        song_name = entry["master_metadata_track_name"]
        combined_name = f"{artist_name} : {song_name}"
        songs_listen_count[combined_name] += 1

    # Exclude the specified artists
    if exclude_artist_list:
        songs_listen_count = {
            key: value
            for key, value in songs_listen_count.items()
            if not any(artist.lower() in key.lower() for artist in exclude_artist_list)
        }

    top_songs = sorted(songs_listen_count.items(), key=lambda x: x[1], reverse=True)[
        :num_top_songs
    ]

    song_artist_names = [item[0] for item in top_songs]
    listen_counts = [item[1] for item in top_songs]

    plt.figure(figsize=(12, 8))
    plt.barh(song_artist_names, listen_counts, color="skyblue")
    plt.xlabel("Listen Counts")
    plt.ylabel("Artist : Song")
    plt.title(
        f'Top {num_top_songs} Songs of All Time (Excluding {", ".join(exclude_artist_list)})'
    )
    plt.gca().invert_yaxis()
    plt.tight_layout()

    # Save the plot to a file
    plt.savefig("static/top_songs_plot.png")
    plt.close()

    # Return the top songs data for rendering in the template
    return top_songs


# def plot_monthly_listen_count(artist_name):
#     # Filter data for the specified artist's songs
#     artist_songs = [
#         entry
#         for entry in data
#         if artist_name.lower() in entry["master_metadata_album_artist_name"].lower()
#     ]

#     # Group data by month
#     monthly_listen_count = defaultdict(int)

#     for entry in artist_songs:
#         timestamp_str = entry["ts"]
#         timestamp = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%SZ")
#         month_year = timestamp.strftime("%Y-%m")
#         monthly_listen_count[month_year] += 1

#     # Extract months and listen counts
#     months = list(monthly_listen_count.keys())
#     listen_counts = list(monthly_listen_count.values())

#     plt.figure(figsize=(12, 8))
#     bars = plt.bar(months, listen_counts, color="lightblue")
#     plt.xlabel("Month")
#     plt.ylabel("Listen Counts")
#     plt.title(f"Monthly Listen Count of {artist_name} Songs")
#     plt.xticks(rotation=45, ha="right")

#     # Annotate each bar with the listen count
#     for i, bar in enumerate(bars):
#         height = bar.get_height()
#         plt.text(
#             bar.get_x() + bar.get_width() / 2,
#             height + 5,
#             f"{height}",
#             ha="center",
#             va="bottom",
#             color="black",
#         )

#     plt.tight_layout()

#     # Save the plot to a file
#     plt.savefig("static/monthly_listen_count_plot.png")
#     plt.close()

#     # Return the monthly listen count data for rendering in the template
#     return monthly_listen_count


def plot_monthly_listen_count(artist_name):
    # Filter data for the specified artist's songs
    artist_songs = [
        entry
        for entry in data
        if entry.get("master_metadata_album_artist_name")
        and artist_name.lower() in entry["master_metadata_album_artist_name"].lower()
    ]

    # Group data by month
    monthly_listen_count = defaultdict(int)

    for entry in artist_songs:
        timestamp_str = entry["ts"]
        timestamp = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%SZ")
        month_year = timestamp.strftime("%Y-%m")
        monthly_listen_count[month_year] += 1

    # Extract months and listen counts
    months = list(monthly_listen_count.keys())
    listen_counts = list(monthly_listen_count.values())

    plt.figure(figsize=(12, 8))
    bars = plt.bar(months, listen_counts, color="lightblue")
    plt.xlabel("Month")
    plt.ylabel("Listen Counts")
    plt.title(f"Monthly Listen Count of {artist_name} Songs")
    plt.xticks(rotation=45, ha="right")

    # Annotate each bar with the listen count
    for i, bar in enumerate(bars):
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            height + 5,
            f"{height}",
            ha="center",
            va="bottom",
            color="black",
        )

    plt.tight_layout()

    # Save the plot to a file
    plt.savefig("static/monthly_listen_count_plot.png")
    plt.close()

    # Return the monthly listen count data for rendering in the template
    return months, listen_counts


# Route to the home page
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        num_top_songs = int(request.form["num_top_songs"])
        if 1 <= num_top_songs <= 50:
            return redirect(url_for("top_songs", num_top_songs=num_top_songs))
        else:
            return "Error: Number of top songs must be between 1 and 50."

    return render_template("home.html")


@app.route("/top_songs", methods=["GET", "POST"])
def top_songs():
    num_top_songs = int(
        request.args.get("num_top_songs", 10)
    )  # Default to 10 if not provided or invalid
    exclude_artists = request.args.get("exclude_artists", "")

    try:
        exclude_artist_list = (
            [artist.strip() for artist in exclude_artists.split(",")]
            if exclude_artists
            else []
        )
        top_songs_data = plot_top_songs(num_top_songs, exclude_artist_list)
        return render_template(
            "top_songs.html",
            top_songs=top_songs_data,
            num_top_songs=num_top_songs,
            exclude_artists=exclude_artists,
        )
    except ValueError as e:
        return f"Error: {e}"


# @app.route("/top_songs")
# def top_songs():
#     num_top_songs = int(
#         request.args.get("num_top_songs", 10)
#     )  # Default to 10 if not provided or invalid
#     try:
#         top_songs_data = plot_top_songs(num_top_songs)
#         return render_template("top_songs.html", top_songs=top_songs_data)
#     except ValueError as e:
#         return f"Error: {e}"


# Add a new route for the monthly listen count
@app.route("/monthly_listen_count", methods=["GET", "POST"])
def monthly_listen_count():
    if request.method == "POST":
        artist_name = request.form.get("artist_name")
        if not artist_name:
            return "Please provide an artist name."

        try:
            monthly_listen_count_data = plot_monthly_listen_count(artist_name)
            return render_template(
                "monthly_listen_count.html",
                monthly_listen_count=monthly_listen_count_data,
            )
        except ValueError as e:
            return f"Error: {e}"

    return render_template("monthly_listen_count.html")


if __name__ == "__main__":
    app.run(debug=True)
