from urllib.parse import urlencode, urlparse, parse_qsl
import requests
import pprint
import pandas as pd

# Use unique google API key
GOOGLE_API_KEY = "Your Unique ID"

# GoogleMapsClient: Gets location from user, and downloads local information based on query 
class GoogleMapsClient(object):
    lat = None
    lng = None
    data_type = 'json'
    lookup_location = None
    api_key = None
    
    def __init__(self, api_key=None, address=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if api_key == None:
            raise Exception("API key is required")
        self.api_key = api_key
        self.lookup_location = address
        if self.lookup_location != None:
            self.get_coordinate()
    
    # Gets latitude and longitude of location given by user
    def get_coordinate(self):
        endpoint = f"https://maps.googleapis.com/maps/api/geocode/{self.data_type}"
        params = {"address": self.lookup_location, "key": self.api_key}
        url_params = urlencode(params)
        url = f"{endpoint}?{url_params}"

        # Checks for valid url
        r = requests.get(url)
        if r.status_code not in range(200,299):
            return {}
        latlng={}
        try:
            latlng = r.json()['results'][0]['geometry']['location']
        except:
            pass
        lat,lng = latlng.get("lat"), latlng.get("lng")
        self.lat = lat
        self.lng = lng
        return lat,lng
    
    # Searches and returns local information(JSON) from the given keyword and radius
    # keyword: The place of interest a user wants to know more information about (Malls, Restraunts, etc..)
    # radius: the radius around the given address the user wants to search
    def search(self, keyword="Italian Food", radius=5000, location=None):
        lat, lng = self.lat, self.lng
        if location != None:
            lat, lng = self.get_coordinate(location=location)
        endpoint = f"https://maps.googleapis.com/maps/api/place/nearbysearch/{self.data_type}"
        params = {
            "key": self.api_key,
            "location": f"{lat},{lng}",
            "radius": radius,
            "keyword": keyword
        }
        encoded_parameters = urlencode(params)
        places_url = f"{endpoint}?{encoded_parameters}"
        r = requests.get(places_url)
        if r.status_code not in range(200, 299):
            return {}
        return r.json()
    
    # Returns specific information from restraunts the user was looking for within the field
    # place_id: A specific id google gives places of interest
    # fields: different fields of information to be returned about the place of interest
    def detail(self, place_id="ChIJlXOKcDC3j4ARzal-5j-p-FY", fields=["name", "rating", "formatted_phone_number", "formatted_address"]):
        detail_base_endpoint = f"https://maps.googleapis.com/maps/api/place/details/{self.data_type}"
        detail_params = {
            "place_id": f"{place_id}",
            "fields" : ",".join(fields),
            "key": self.api_key
        }
        detail_encoded_parameters = urlencode(detail_params)
        detail_url = f"{detail_base_endpoint}?{detail_encoded_parameters}"
        r = requests.get(detail_url)
        if r.status_code not in range(200, 299):
            return {}
        return r.json()['result']

    # Downloads information of the place/s of interest into a CSV file
    # keyword: The place of interest a user wants to know more information about (Malls, Restraunts, etc..)
    # radius: the radius around the given address the user wants to search
    def download_info(self, keyword="Mexican Food", radius=2000):
        search_info = self.search(keyword, radius)
        results = search_info['results']
        
        if len(results) > 0:
            place_ids = set()
            for result in results:
                _id = result['place_id']
                place_ids.add(_id)

            output = f"nearby_{keyword}_from_{self.lookup_location}.csv"
            places_data = []

            for place_id in place_ids:
                temp_place_data = self.detail(place_id)
                places_data.append(temp_place_data)

            df = pd.pandas.DataFrame(places_data)
            print(df.head())
            df.to_csv(output, index=False)
        else:
            print(f"No results for {keyword} in {self.lookup_location}")
