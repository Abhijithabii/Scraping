from .models import *

from django.conf import settings

from pymongo import GEOSPHERE

import pymongo


def get_db():
    db = settings.DB
    return db


def create_indexes():
    db = get_db()
    providers_data_collection = db["provider_data"]
    ukpostcodes = db["ukpostcodes"]
    providers_data_collection.drop_indexes()
    providers_data_collection.create_index([("hospital_details.location", "2dsphere")])
    ukpostcodes.create_index([("postcode", pymongo.TEXT)])
    # providers_data_collection.create_index([("location.coordinates", GEOSPHERE)])
    providers_data_collection.create_index(
        [
            ("speciality", pymongo.TEXT),
            ("sub_speciality", pymongo.TEXT),
            ("service_types", pymongo.TEXT),
        ],
    )




# def save_data_from_excel(file_path):
#     df = pd.read_excel(file_path)
#     for index, row in df.iterrows():
#         speciality_name = row['Speciality']
#         subspeciality_name = row['Subspeciality']

#         speciality, created = Speciality.objects.get_or_create(speciality=speciality_name)
        
#         subspeciality, subspeciality_created = Subspeciality.objects.get_or_create(
#             sub_speciality=subspeciality_name, speciality_fk=speciality
#         )
#         if not subspeciality_created:
#             subspeciality.sub_speciality = subspeciality_name
#             subspeciality.save()

#     print("Data has been successfully saved.")