import requests
import sqlite3

# Seeds the specified sqlite DB with the 2023 F1 racing schedule

DB = "f1.sqlite"
db = sqlite3.connect(DB)
cur = db.cursor()
cur.execute("CREATE TABLE tracks(name, record_driver_name, record_driver_flag, record_driver_team, record_time, record_year)")
cur.execute("CREATE TABLE events(sent, name, type, start, flag, track, sessions)")

re = requests.get("https://raw.githubusercontent.com/MarkusTheOrt/f1-calendar/main/calendar.json")
json = re.json()

tracks = []
events = []
for e in json["events"]:
    # Events: sent, name, type, start, flag, track, sessions
    event = [0, e["name"], e["type"], e["start"], e["prefix"], e["racetrack"]["name"]]
    sessions = []
    for s in e["sessions"]:
        sessions.append([s["type"], s["name"], s["start"], s["duration"]])
    event += [str(sessions)]
    events += [event]

    # Tracks: Track name, driver name, driver flag, driver team, record time, record year
    r = e["racetrack"]
    track = [r["name"]]
    if "recordTime" in r:
        track.extend([r["recordTime"]["driver"]["name"], r["recordTime"]["driver"]["prefix"], r["recordTime"]["driver"]["team"], r["recordTime"]["time"]["value"], r["recordTime"]["year"]])
    else:
        track.extend([0, 0, 0, 0, 0])
    tracks.append(track)

cur.executemany("INSERT INTO tracks VALUES(?, ?, ?, ?, ?, ?)", tracks)
cur.executemany("INSERT INTO events VALUES(?, ?, ?, ?, ?, ?, ?)", events)
db.commit()
