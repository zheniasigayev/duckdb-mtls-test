import pandas as pd
import numpy as np
from datetime import datetime
import random
import string

# Instructions
# 1. `brew install python`
# 2. `python3 -m venv venv`
# 3. `source venv/bin/activate`
# 4. `pip install pandas pyarrow numpy`
# 5. `python generate_parquet.py`

def generate_weather_data(file_size_mb=20):
    """Generate random weather data to create approximately the specified file size."""

    # Helper functions for generating random data
    def random_station_id():
        """Generate a random weather station ID."""
        return ''.join(random.choices(string.ascii_uppercase, k=3)) + '-' + ''.join(random.choices(string.digits, k=4))

    def random_city_name():
        """Generate a random city name."""
        cities = ["Springfield", "Riverdale", "Lakeside", "Mountainview", "Westport",
                  "Oakridge", "Newport", "Fairview", "Brighton", "Cedar Hills",
                  "Millville", "Pleasantville", "Greenfield", "Summerdale", "Winterfell",
                  "Sunnyvale", "Brookside", "Highland", "Meadowbrook", "Pinecrest"]
        return random.choice(cities)

    def random_weather_condition(temp):
        """Generate appropriate weather condition based on temperature."""
        if temp < 32:
            return random.choice(["Snow", "Sleet", "Freezing Rain", "Blizzard", "Cloudy"])
        elif temp < 50:
            return random.choice(["Rain", "Drizzle", "Overcast", "Partly Cloudy", "Cloudy"])
        elif temp < 75:
            return random.choice(["Partly Cloudy", "Mostly Sunny", "Clear", "Sunny", "Mild"])
        else:
            return random.choice(["Sunny", "Hot", "Clear", "Hazy", "Partly Cloudy"])

    # Parameters that affect file size
    # Adjust these to reach desired file size
    num_stations = 100
    days = 365
    readings_per_day = 24  # hourly readings

    # Create template for one day of readings
    single_day_times = pd.date_range(
        start='2023-01-01',
        periods=readings_per_day,
        freq='H'
    )

    # Create date range for a year
    all_dates = pd.date_range(
        start='2023-01-01',
        periods=days,
        freq='D'
    )

    # Generate station data
    stations = []
    for i in range(num_stations):
        station_id = random_station_id()
        latitude = random.uniform(25.0, 49.0)  # US latitude range
        longitude = random.uniform(-125.0, -65.0)  # US longitude range
        elevation = random.uniform(0, 14000)  # elevation in feet
        city = random_city_name()
        region = random.choice(["North", "South", "East", "West", "Central"])
        country = "United States"

        stations.append({
            'station_id': station_id,
            'latitude': latitude,
            'longitude': longitude,
            'elevation': elevation,
            'city': city,
            'region': region,
            'country': country
        })

    stations_df = pd.DataFrame(stations)

    # Generate weather readings
    all_data = []

    for station in stations_df.itertuples():
        # Base temperature profile for this station
        base_temp = random.uniform(45, 75)
        temp_amplitude = random.uniform(10, 30)

        for day in all_dates:
            # Seasonal variation (sinusoidal)
            day_of_year = day.dayofyear
            seasonal_factor = np.cos(2 * np.pi * (day_of_year - 172) / 365)  # Peaks in summer
            daily_base = base_temp + (seasonal_factor * temp_amplitude)

            for hour_idx, timestamp in enumerate(single_day_times):
                # Create timestamp for this specific reading
                current_time = datetime(
                    day.year, day.month, day.day,
                    timestamp.hour, timestamp.minute, timestamp.second
                )

                # Hourly variation (sinusoidal)
                hourly_factor = np.cos(2 * np.pi * (hour_idx - 14) / 24)  # Peaks at 2pm

                # Add some randomness
                random_factor = random.uniform(-5, 5)

                # Calculate temperature
                temperature = daily_base + (hourly_factor * 10) + random_factor

                # Other weather metrics based on temperature and randomness
                humidity = max(0, min(100, 100 - temperature + random.uniform(-20, 20)))
                wind_speed = random.uniform(0, 35)
                wind_direction = random.uniform(0, 360)
                pressure = random.uniform(980, 1040)
                precipitation = max(0, random.uniform(-0.1, 0.5))
                visibility = random.uniform(0.1, 15)
                cloud_cover = random.uniform(0, 100)
                uv_index = max(0, min(12, (temperature - 40) / 10 + random.uniform(-2, 5)))
                dew_point = temperature - ((100 - humidity) / 5) + random.uniform(-3, 3)

                # Generate weather condition based on temperature
                weather_condition = random_weather_condition(temperature)

                # Generate air quality and additional metrics
                air_quality_index = random.uniform(0, 300)
                soil_moisture = random.uniform(0, 100)
                solar_radiation = max(0, temperature * 2 + random.uniform(-50, 150))

                # Add data point to collection
                all_data.append({
                    'station_id': station.station_id,
                    'latitude': station.latitude,
                    'longitude': station.longitude,
                    'elevation': station.elevation,
                    'city': station.city,
                    'region': station.region,
                    'country': station.country,
                    'timestamp': int(current_time.timestamp() * 1000),
                    'datetime': current_time,
                    'temperature': round(temperature, 1),
                    'feels_like': round(temperature - (wind_speed * 0.1) + (humidity * 0.05) - 5, 1),
                    'humidity': round(humidity, 1),
                    'wind_speed': round(wind_speed, 1),
                    'wind_direction': round(wind_direction, 1),
                    'pressure': round(pressure, 1),
                    'precipitation': round(precipitation, 2),
                    'visibility': round(visibility, 1),
                    'cloud_cover': round(cloud_cover, 1),
                    'weather_condition': weather_condition,
                    'uv_index': round(uv_index, 1),
                    'dew_point': round(dew_point, 1),
                    'air_quality_index': round(air_quality_index, 1),
                    'soil_moisture': round(soil_moisture, 1),
                    'solar_radiation': round(solar_radiation, 1),
                    'forecast_day1_high': round(temperature + random.uniform(0, 15), 1),
                    'forecast_day1_low': round(temperature - random.uniform(5, 15), 1),
                    'forecast_day1_condition': random_weather_condition(temperature + random.uniform(-5, 5)),
                    'forecast_day2_high': round(temperature + random.uniform(-10, 15), 1),
                    'forecast_day2_low': round(temperature - random.uniform(5, 20), 1),
                    'forecast_day2_condition': random_weather_condition(temperature + random.uniform(-10, 10)),
                    'metadata': f"Weather data for {station.city} region. Station ID: {station.station_id}. " +
                    f"Located at lat: {station.latitude}, long: {station.longitude}, elev: {station.elevation}ft."
                })

    # Create DataFrame
    weather_df = pd.DataFrame(all_data)

    print(f"Generated {len(weather_df)} rows of weather data")
    print(f"DataFrame memory usage: {weather_df.memory_usage(deep=True).sum() / (1024*1024):.2f} MB")

    # Save to parquet file
    output_file = 'data.parquet'
    weather_df.to_parquet(output_file, engine='pyarrow', compression='snappy')

    # Report file size
    import os
    file_size_mb = os.path.getsize(output_file) / (1024 * 1024)
    print(f"Generated parquet file size: {file_size_mb:.2f} MB")

    return output_file

# Generate the weather data file
if __name__ == "__main__":
    output_file = generate_weather_data(20)
    print(f"Weather data saved to {output_file}")
