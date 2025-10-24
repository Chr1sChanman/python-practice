'''
Understand:
    Input: List of tuples
    Output: Hashmap with Companies as keys and screentime as values
    Constraints: N/A
    Edge Cases: Empty list, idk
Plan:
    Create a hashmap for results
    Iterate through the list using tuple unpacking/extracting
        Equal the key(company) to the amount of time spent on that app
    Return that hashmap

'''

def track_screen_time(logs):
    res = {}
    for app, minutes in logs:
        if app in res:
            res[app] += minutes
        else:
            res[app] = minutes
    sorted_data = dict(sorted(res.items(), key=lambda item: item[1], reverse=True))
    return list(sorted_data.keys())[0]

logs = [("Instagram", 30), ("YouTube", 20), ("Instagram", 25), ("Snapchat", 15), ("YouTube", 10)]
logs_2 = [("Twitter", 10), ("Reddit", 20), ("Twitter", 15), ("Instagram", 35)]
logs_3 = [("TikTok", 40), ("TikTok", 50), ("YouTube", 60), ("Snapchat", 25)]

print(track_screen_time(logs))
print(track_screen_time(logs_2))
print(track_screen_time(logs_3))

def most_varied_app(app_usage):
    name = []
    max_range = None
    for i,j in app_usage.items():
        if not j:
            continue
        curr = max(j) - min(j)

        if max_range is None or curr > max_range:
            max_range = curr
            name = [i]
        elif curr == max_range:
            name.append(i)
    return name
            

app_usage = {
    "Instagram": [60, 55, 65, 60, 70, 55, 60],
    "YouTube": [100, 120, 110, 100, 115, 105, 120],
    "Snapchat": [30, 35, 25, 30, 40, 35, 30]
}

app_usage_2 = {
    "Twitter": [15, 15, 15, 15, 15, 15, 15],
    "Reddit": [45, 50, 55, 50, 45, 50, 55],
    "Facebook": [80, 85, 80, 85, 80, 85, 80]
}

app_usage_3 = {
    "TikTok": [80, 100, 90, 85, 95, 105, 90],
    "Spotify": [40, 45, 50, 45, 40, 45, 50],
    "WhatsApp": [60, 60, 60, 60, 60, 60, 60]
}

app_usage_4 = {
    "TikTok": [80, 100, 90, 85, 95, 105, 90],
    "Spotify": [40, 45, 50, 45, 40, 45, 50],
    "WhatsApp": [80, 100, 90, 85, 95, 105, 90]
}

print(most_varied_app(app_usage))
print(most_varied_app(app_usage_2))
print(most_varied_app(app_usage_3))
print(most_varied_app(app_usage_4))