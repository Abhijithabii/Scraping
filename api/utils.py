from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut
from geopy.distance import geodesic

from django.conf import settings

from Crypto.Cipher import AES
from bson import ObjectId

from api.db_utils import get_db

import json
import datetime
import os
import jwt
import requests
import base64
import pandas as pd
import requests
import re

db = get_db()
ukpostcodes_collection = db["ukpostcodes"]

def validate_postcode(input_postcode_without_spaces):

    if len(input_postcode_without_spaces) == 5:
        part1 = input_postcode_without_spaces[:2]
        part2 = input_postcode_without_spaces[2:]
    elif len(input_postcode_without_spaces) == 6:
        part1 = input_postcode_without_spaces[:3]
        part2 = input_postcode_without_spaces[3:]
    elif len(input_postcode_without_spaces) == 7:
        part1 = input_postcode_without_spaces[:4]
        part2 = input_postcode_without_spaces[4:]
    else:
        response_data = {
            'valid': False,
            'error': 'Invalid UK postcode',
        }
        return response_data

    uk_postcode = ukpostcodes_collection.find_one({
        'postcode': {'$eq': f"{part1} {part2}"}
    })
    if uk_postcode:
        response_data = {
            'valid': True,
            'latitude': uk_postcode['latitude'],
            'longitude': uk_postcode['longitude'],
        }
    else:
        response_data = {
            'valid': False,
            'error': 'Invalid UK postcode',
        }
    return response_data


def meters_to_miles(meters):
    miles_conversion_factor = 0.000621371
    miles = meters * miles_conversion_factor
    return miles


def generate_tokens(user_id):
    SECRET_KEY = os.getenv("JWT_SECRET_KEY", "secrets")
    access_payload = {
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=1),
        'iat': datetime.datetime.utcnow(),
    }
    access_token = jwt.encode(access_payload, SECRET_KEY, algorithm='HS256')

    refresh_payload = {
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1),
        'iat': datetime.datetime.utcnow(),
    }
    refresh_token = jwt.encode(refresh_payload, SECRET_KEY, algorithm='HS256')
    return {'access_token': access_token, 'refresh_token': refresh_token}




def encrypt_ff3(key, counter, data):
    encryptor = AES.new(key, AES.MODE_CTR, counter=counter)
    ciphertext = encryptor.encrypt(data.encode("utf-8"))
    return ciphertext.hex()

def decrypt_ff3(key, counter, ciphertext):
    decryptor = AES.new(key, AES.MODE_CTR, counter=counter)
    plaintext = decryptor.decrypt(bytes.fromhex(ciphertext)).decode("utf-8")
    return plaintext


def calculate_distance(search_coords, doctor_coords):
    if search_coords and doctor_coords:
        return geodesic(search_coords, doctor_coords).miles
    else:
        return None


class CombinedJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        if isinstance(o, datetime.datetime):
            return o.isoformat()
        return json.JSONEncoder.default(self, o)


# def postcode_to_coordinates(address, region=None):
#     api_key = os.getenv("GOOGLE_MAPS_API_KEY")
#     base_url = "https://maps.googleapis.com/maps/api/geocode/json?"
#     params = {"address": address, "key": api_key}
#     if region:
#         params["region"] = region

#     response = requests.get(base_url, params=params)
#     data = response.json()

#     if data["status"] == "OK":
#         latitude = data["results"][0]["geometry"]["location"]["lat"]
#         longitude = data["results"][0]["geometry"]["location"]["lng"]
#         return {"longitude": longitude, "latitude": latitude}
#     else:

#         return {"error": data["status"]}
    

def postcode_to_coordinates(address, region=None):
    
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    # api_key = "AIzaSyD_p3o701GjKyYwcAuc_dFr-LIEORd_RBU"
    if not api_key:
        return {"error": "API key missing"}

    base_url = "https://maps.googleapis.com/maps/api/geocode/json?"
    params = {"address": address, "key": api_key}
    if region:
        params["region"] = region

    try:
        response = requests.get(base_url, params=params)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        data = response.json()
    except requests.RequestException as e:
        return {"error": "API request failed", 'valid': False,}

    if "results" in data and data["results"]:
        latitude = data["results"][0]["geometry"]["location"]["lat"]
        longitude = data["results"][0]["geometry"]["location"]["lng"]
        return {"longitude": longitude, "latitude": latitude, 'valid': True,}
    else:
        error_message = data.get("error_message", "Unknown error")
        return {"error": data["status"], "error_message": error_message, 'valid': False,}

    

# def postcode_to_coordinates(address, region=None):
#     geolocator = Nominatim(user_agent="Medzen")

#     if region:
#         address += f", {region}"

#     try:
#         location = geolocator.geocode(address)
#         # Rest of the code
#     except Exception as e:
#         print(f"Error during geocoding: {str(e)}")
#         return {"error": "Geocoding error"}


#     if location:
#         latitude = location.latitude
#         longitude = location.longitude
#         return {"longitude": longitude, "latitude": latitude}
#     else:
#         return {"error": "Address not found"}


def sanitize_cache_key(key):
    encoded_key = base64.b64encode(key.encode()).decode()
    return encoded_key



def validate_coordinates(coordinates):
    if len(coordinates) != 2:
        return False

    lat, lng = coordinates[1], coordinates[0]
    if not (-90 <= lat <= 90):
        return False
    if not (-180 <= lng <= 180):
        return False
    return True



def get_location(ip_address, api_key):
    base_url = f"http://api.ipstack.com/{ip_address}"
    params = {'access_key': api_key}
 
    try:
        response = requests.get(base_url, params=params)
        data = response.json()
 
        if 'error' in data:
            print(f"Error: {data['error']['info']}")
        else:
            city = data.get('city', 'N/A')
            region = data.get('region_name', 'N/A')
            country = data.get('country_name', 'N/A')
            latitude = data.get('latitude', 'N/A')
            longitude = data.get('longitude', 'N/A')
 
            print(f"IP Address: {ip_address}")
            print(f"City: {city}")
            print(f"Region: {region}")
            print(f"Country: {country}")
            print(f"Latitude: {latitude}")
            print(f"Longitude: {longitude}")
 
    except Exception as e:
        print(f"Error: {e}")





# def user_locaton_and_ip_address(request):
#     try:
#         ip_response = requests.get('https://api64.ipify.org?format=json')
#         if ip_response.status_code == 200:
#             data = ip_response.json()
#             ip_address = data.get('ip')
#             print(ip_address, '-----search view')
#         else:
#             print(f"Request failed with status code: {ip_response.status_code}")
#     except requests.RequestException as e:
#         print(f"Error: {e}")
#     location_response = requests.get(f'https://get.geojs.io/v1/ip/geo/{ip_address}.json')
#     if location_response.status_code == 200:
#         data = location_response.json()
#         # Extract relevant location information from the JSON response
#         country = data.get('country')
#         city = data.get('city')
#         print(country, city, '-----search')
#     data = {
#         "ip_address" : ip_address,
#         "country" : country,
#         "city" : city,
#     }
#     return data
        



def user_location_and_ip_address(request):
    try:
        ip_address = request.META.get('REMOTE_ADDR')
        print(ip_address, '-----search view')
        
        location_response = requests.get(f'https://get.geojs.io/v1/ip/geo/{ip_address}.json')
        if location_response.status_code == 200:
            data = location_response.json()
            # Extract relevant location information from the JSON response
            country = data.get('country')
            city = data.get('city')
            print(country, city, '-----search')
            
            return {
                "ip_address" : ip_address,
                "country" : country,
                "city" : city,
            }
        else:
            print(f"Location request failed with status code: {location_response.status_code}")
            return None
    except Exception as e:
        print(f"Error: {e}")
        return None