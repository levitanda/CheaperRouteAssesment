import pandas as pd
import geopy
from geopy.geocoders import Nominatim
import time

FUEL_PRICES = pd.read_csv("/app/Routes_Finder/cheaper_route/fuel-prices-for-be-assessment.csv")
geolocator = Nominatim(user_agent="dalevitan17@gmail.com")

def get_lat_lon(address):
    try:
        location = geolocator.geocode(address)
        if location:
            return location.latitude, location.longitude
        else:
            return None, None
    except geopy.exc.GeocoderUnavailable:
        # Delay to avoid rate-limiting and retry
        time.sleep(10)  
        return get_lat_lon(address)

def add_lat_lon_to_truckstops(df):
    counter = 0
    for index, row in df.iterrows():
        if row['OPIS Truckstop ID'] == 72950:
            print("stop")     
        if pd.isnull(row['Latitude']) or pd.isnull(row['Longitude']):
            address = row['City'] + ", " + row['State']
            lat, lon = get_lat_lon(address)
            counter += 1
            df.at[index, 'Latitude'] = lat
            df.at[index, 'Longitude'] = lon
            if counter % 60 == 0:
                FUEL_PRICES.to_csv("/app/Routes_Finder/cheaper_route/fuel-prices-for-be-assessment.csv", index=False)
                print(f"Processed 60 addresses")
        else:
            print(f"Skipping {row['Truckstop Name']} as latitude and longitude are already available.")
    return df

FUEL_PRICES = add_lat_lon_to_truckstops(FUEL_PRICES)
FUEL_PRICES.to_csv("/app/Routes_Finder/cheaper_route/fuel-prices-for-be-assessment.csv", index=False)
print('The latitude and longitude are updated')  
