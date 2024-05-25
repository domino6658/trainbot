import csv
from collections import Counter

def topStats(user, stat):
    with open(f'utils/trainlogger/userdata/{user}.csv', newline='') as csvfile:
        reader = csv.reader(csvfile)
        
        # Counters to keep track of line and station frequencies
        line_counter = Counter()
        station_counter = Counter()
        set_counter = Counter()
        date_counter = Counter()
        type_counter = Counter()

        # Process each row in the CSV
        for row in reader:
            # Row format: LogID, TrainID, TrainType, Date, Line, Start, End
            line = row[4]
            start_station = row[5]
            end_station = row[6]
            set = row[1]
            type = row[2]
            date = row[3]
            # Update counters
            line_counter.update([line])
            station_counter.update([start_station, end_station])
            set_counter.update([set])
            type_counter.update([type])
            date_counter.update([date])

        # Get the 10 most common lines
        most_common_lines = line_counter.most_common(10)
        most_common_stations = station_counter.most_common(10)
        most_common_sets = set_counter.most_common(10)
        most_common_types = type_counter.most_common(10)
        most_common_dates = date_counter.most_common(10)

        # Get the 10 most common stations

        # Prepare the results as a list
        results = []

        # Append the most common lines to the results list
        if stat == "lines":
            for line, count in most_common_lines:
                results.append(f"{line}: {count} times")
        if stat == "stations":
            for station, count in most_common_stations:
                results.append(f"{station}: {count} times")
        if stat == "sets":
            for set, count in most_common_sets:
                results.append(f"{set}: {count} times")
        if stat == "types":
            for type, count in most_common_types:
                results.append(f"{type}: {count} times")
        if stat == "dates":
            for date, count in most_common_dates:
                results.append(f"{date}: {count} times")
        # # Append the most common stations to the results list
        # results.append("\nThe 10 most frequent stations are:")
        # for station, count in most_common_stations:
        #     results.append(f"{station}: {count} times")
        print(results)
        return results
