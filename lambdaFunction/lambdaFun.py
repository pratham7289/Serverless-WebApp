import json
import boto3
import random
import string
from datetime import datetime

ddb = boto3.resource('dynamodb')
table_name = "Rides"
table = ddb.Table(table_name)

fleet = [
    {
        "Name": "Bucephalus",
        "Color": "Golden",
        "Gender": "Male"
    },
    {
        "Name": "Shadowfax",
        "Color": "White",
        "Gender": "Male"
    },
    {
        "Name": "Rocinante",
        "Color": "Yellow",
        "Gender": "Female"
    }
]

def lambda_handler(event, context):
    print(f"event: {event}")
    #checking if the user is authorized
    if "authorizer" not in event["requestContext"]:
        return error_response("Authorization not configured")
        
    #Generating a unique ride RI for each ride booked
    ride_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=16))
    print(f"Received event ({ride_id}): {event}")
   
   # Fetching the username of the rider who booked the ride
    username = event["requestContext"]["authorizer"]["claims"]["cognito:username"]
   
   #formatting the event object's body attribute as JSON and loads it into a Python dictionary
    request_body = json.loads(event["body"])
    
    pickup_location = request_body["PickupLocation"]

    unicorn = find_unicorn(pickup_location)
    
    #Calls the record_ride function, passing in the ride ID, Cognito username, and unicorn.
    record_ride(ride_id, username, unicorn)

    response = {
        "statusCode": 201,
        "body": json.dumps({
            "RideId": ride_id,
            "Unicorn": unicorn,
            "UnicornName": unicorn["Name"],
            "Eta": "30 seconds",
            "Rider": username
        }),
        "headers": {
            "Access-Control-Allow-Origin": "*"
        }
    }

    return response

def find_unicorn(pickup_location):
    print(f"Finding unicorn for {pickup_location['Latitude']}, {pickup_location['Longitude']}")
    return random.choice(fleet)

#Function to insert records inside dynamoDB
def record_ride(ride_id, username, unicorn):
    table.put_item(
        Item={
            "RideId": ride_id,
            "User": username,
            "Unicorn": unicorn,
            "UnicornName": unicorn["Name"],
            "RequestTime": datetime.now().isoformat()
        }
    )

def error_response(error_message):
    return {
        "statusCode": 500,
        "body": json.dumps({
            "Error": error_message
        }),
        "headers": {
            "Access-Control-Allow-Origin": "*"
        }
    }



