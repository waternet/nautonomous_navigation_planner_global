import requests, json
import ww #temp to hide urls

URL_TRACK = "https://waternet.globalguidesystems.com/api/v0/object/OBJECTID_VALUE/track?day=DATE_VALUE"
URL_OBJECTS = "https://waternet.globalguidesystems.com/api/v0/object?left=LEFT_VALUE&top=TOP_VALUE&right=RIGHT_VALUE&bottom=BOTTOM_VALUE&age=AGE_VALUE"

from boat import Boat
from boat_state import BoatState

import datetime

import utm_helper

class API:
    def __init__(self):        
        self._token = ""
        self._user = ww.USER
        self._password = ww.PASS

    def _has_token(self):
        return self._token!=""

    def _authenticate(self):
        data = '{"userName":"%s", "password": "%s" }' % (self._user, self._password)
        auth_resp = requests.post(ww.URL_AUTH, data=data)
        auth_json = json.loads(auth_resp.text)
        self._token = auth_json['token']

    def _generate_url_track(self, object_id, date):
        return URL_TRACK.replace('OBJECTID_VALUE', object_id).replace('DATE_VALUE', date)

    def _generate_url_objects(self, left, top, right, bottom, age):
        return URL_OBJECTS.replace('LEFT_VALUE', left).replace('TOP_VALUE', top).replace('RIGHT_VALUE', right).replace('BOTTOM_VALUE', bottom).replace('AGE_VALUE', age)

    def track_request(self, object_id, date):
        if not self._has_token():
            self._authenticate()

        url = self._generate_url_track(object_id, date)
        track_resp = requests.get(url, headers={'Authorization': self._token})
        track_json = json.loads(track_resp.text)

        boat_states = []
        # invert list order before returning list.
        for data_item in track_json[::-1]:
            lat = data_item['lat']
            lon = data_item['lon']
	    #print "Track request " + str(lat) + " "+ str(lon)
            if(lat > 55 or lat < 50): # filter out weird coordinates
                continue

            easting, northing = utm_helper.convert_GPS_coordinate_to_UTM_position(lat, lon)

            boat_states.append(BoatState(easting, northing, data_item['direction'], data_item['speed'], data_item['timestamp']))

        return boat_states

    def objects_request(self, left, top, right, bottom, age):
        if not self._has_token():
            self._authenticate()

        url = self._generate_url_objects(left, top, right, bottom, age)
        objects_resp = requests.get(url, headers={'Authorization': self._token})
        objects_json = json.loads(objects_resp.text)
        # invert list order before returning list.
        print objects_json
        boats = []
        for data_item in objects_json:
            boat_state = BoatState(data_item['Position']['y'], data_item['Position']['x'], data_item['Direction'], data_item['Speed'], data_item['Lastupdate'])
            boats.append(Boat(data_item['Id'], data_item['Name'], data_item['Type'], data_item['Length'], data_item['Width'], boat_state))
        
        # invert list order before returning list.
        return boats

    def all_objects_history_request(self, days):
        boats = self.objects_request("4.88", "52.36", "4.9", "52.38", "10")

        print "No. boats: "  + str(len(boats))

        for boat in boats:
            boat.add_history(self.construct_boat_states_history(boat, days))

       
        return boats

    def requested_objects_history_request(self, days, boats_requested):
        boats = self.objects_request("4.88", "52.36", "4.9", "52.38", "10")

        print "No. boats: "  + str(len(boats))

        for boat in boats:
            if boat.id() in boats_requested:
                boat.add_history(self.construct_boat_states_history(boat, days))

       
        return boats

    def construct_boat_states_history(self, boat, days):
        
        current_day = datetime.date.today()
        current_day -= datetime.timedelta(1) # start with the day before
        current_day -= datetime.timedelta(1) # start with the day before

        boat_states = []

        for i in range(days):
            current_day_string = current_day.strftime('%Y-%m-%d').replace("-0", "-")
            #print current_day_string
            boat_states_request = self.track_request(boat.id(), current_day_string) #old canal boat 244780652
            boat_states.extend(boat_states_request)

            current_day -= datetime.timedelta(1) # Current day is previous day

        return boat_states
