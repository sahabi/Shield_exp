import socket
from geopy.distance import vincenty
from lmcp import LMCPFactory
from afrl.cmasi import EntityState
from afrl.cmasi import AirVehicleState
from afrl.cmasi import AirVehicleConfiguration
from afrl.cmasi import Play
from afrl.cmasi.SessionStatus import SessionStatus
from PyMASE import UAV, Location, get_args
from Shield import Shield
import string
from random import choice

stateMap = dict()
playMap = dict()
configMap = dict()

int_loc_map = { 1: (1.5467, -132.556),  2: (1.5467, -132.5623),  3: (1.5361, -132.5480),  4: (1.5467, -132.5479),\
                5: (1.5362, -132.5635),  6: (1.5361, -132.5550),  7: (1.5203, -132.5648),  8: (1.5196, -132.5562),\
                9: (1.5557, -132.5167), 10: (1.5484, -132.5121), 12: (1.5270, -132.5167), 13: (1.5300, -132.5091),\
               11: (1.5300, -132.5240), 15: (1.5400, -132.5240), 14: (1.5370, -132.5100) }


def int_to_bin(num):
    converted = '{0:04b}'.format(num)
    l4 = int(converted[0])
    l3 = int(converted[1])
    l2 = int(converted[2])
    l1 = int(converted[3])
    return (l4, l3, l2, l1)

def bin_to_int(l4, l3, l2, l1):
    l4_ = 0
    l3_ = 0
    l2_ = 0
    l1_ = 0
    if l4 == True:
        l4_ = 1
    if l3 == True:
        l3_ = 1
    if l2 == True:
        l2_ = 1
    if l1 == True:
        l1_ = 1
    num = l1_ + l2_*2 + l3_*4 + l4_*8
    return num

def get_wp(play_map, wp):
    global time, playMap, message, sc_time

    while playMap.get(1) is None:
        message = msg.getObject(sock.recv(2224))
        message_received(message)
        if sc_time - time > 400000:
            time = sc_time
            return wp

    message = msg.getObject(sock.recv(2224))
    message_received(message)
    click_time = playMap.get(1).get_Time()

    if click_time > time:
        time = sc_time
        wp = playMap.get(1).get_PlayID()
        return wp

    while click_time < time:
        message = msg.getObject(sock.recv(2224))
        message_received(message)
        if sc_time - time > 400000:
            time = sc_time
            return wp        
        click_time = playMap.get(1).get_Time() 

    time = sc_time
    wp = playMap.get(1).get_PlayID()
    return wp


def move(uav,loc):
    location = Location(loc[0],loc[1],0,0,'A')
    uav.point_search(location)

def Fuel_monitor(uav):
    fuel_ = uav.get_energy()
    if fuel_ <= 90 and fuel_ != 0:
        fuel = 1
    elif fuel_ > 90:
        fuel = 0
    return fuel

def detect_area(uav, coverage_location):
    uav_location = (stateMap.get(uav.id).get_Location().get_Latitude(), stateMap.get(uav.id).get_Location().get_Longitude())
    if (uav_location[0] <= coverage_location[0] + 0.002 and uav_location[0] >= coverage_location[0] - 0.002\
    and uav_location[1] >= coverage_location[1] - 0.002 and uav_location[1] >= coverage_location[1] - 0.002):
        return 1
    else:
        return 0

def u1_sensor(uav):
    coverage_location = (int_loc_map[1][0],int_loc_map[1][1])
    return detect_area(uav, coverage_location)

def u2_sensor(uav):
    coverage_location = (1.5263,-132.56)
    return detect_area(uav, coverage_location)

def message_received(obj):
    global stateMap
    global configMap
    global playMap
    global commandMap
    global sc_time
    if isinstance(obj ,SessionStatus):
        sc_time = obj.get_ScenarioTime()
    if isinstance(obj ,AirVehicleConfiguration.AirVehicleConfiguration):
        configMap[obj.get_ID()] = obj
    if isinstance(obj, AirVehicleState.AirVehicleState): 
        stateMap[obj.get_ID()] = obj
    if isinstance(obj, Play.Play):
        playMap[obj.get_UAVID()] = obj
    if isinstance(obj, SessionStatus):
        ss = obj

def connect():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = ("localhost", 5555)
    print("connecting to %s port %s") % (server_address)
    sock.connect(server_address)
    print("connected")
    return sock


sock = connect()
msg = LMCPFactory.LMCPFactory()
time = 0
uav_n = 2
UAVs = []

for i in range(0,uav_n):
    UAVs.append(UAV(i+1,sock,stateMap))

flag = 0
while flag != 1:
    flag = 1
    message = msg.getObject(sock.recv(2224))
    message_received(message)
    for i in range(0,uav_n):
        UAVs[i].stateMap = stateMap
        if UAVs[i].stateMap.get(UAVs[i].id) is None:
            flag = 0

current_wp = int_loc_map[1]
current_wp_advers = (stateMap.get(2).get_Location().get_Latitude(), stateMap.get(2).get_Location().get_Longitude())
wp_advers = current_wp_advers
corrected_next_wp = 1
shield = Shield()
advers = [7, 8, 3, 4]
try:
    while True:

        message = msg.getObject(sock.recv(2224))

        message_received(message)
        for i in range(0,uav_n):
            UAVs[i].stateMap = stateMap

        # UAVs[0] = Fuel_monitor(UAVs[0],0,0)

        if (current_wp[0] <= int_loc_map[corrected_next_wp][0] + 0.002 and current_wp[0] >= int_loc_map[corrected_next_wp][0] - 0.002) and \
        (current_wp[1] <= int_loc_map[corrected_next_wp][1] + 0.002 and current_wp[1] >= int_loc_map[corrected_next_wp][1] - 0.002):

            next_wp = get_wp(playMap, corrected_next_wp)
            UAVs[0].state = 0
            fuel_sensor = Fuel_monitor(UAVs[0])
            ugs_1 = u1_sensor(UAVs[1])
            ugs_2 = u2_sensor(UAVs[1])
            # print next_wp

            print 'actual: ', next_wp
            next_wp = int_to_bin(next_wp - 1)
            print 'actual: ', (fuel_sensor, ugs_1, next_wp[0], next_wp[1], next_wp[2], next_wp[3])

            corrected_next_wp = shield.move(fuel_sensor, ugs_1, next_wp[3], next_wp[2], next_wp[1], next_wp[0])
            print 'correction:', corrected_next_wp
            corrected_next_wp = bin_to_int(corrected_next_wp[3], corrected_next_wp[2], corrected_next_wp[1], corrected_next_wp[0])+1

            wp = int_loc_map[corrected_next_wp]
            print 'correction: ', corrected_next_wp

            move(UAVs[0], wp)

        if ((current_wp_advers[0] <= wp_advers[0] + 0.002 and current_wp_advers[0] >= wp_advers[0] - 0.002) and \
        (current_wp_advers[1] <= wp_advers[1] + 0.002 and current_wp_advers[1] >= wp_advers[1] - 0.002)):

            UAVs[1].state = 0
 
            wp_advers = int_loc_map[choice(advers)]

            move(UAVs[1], wp_advers)

        current_wp = (stateMap.get(1).get_Location().get_Latitude(), stateMap.get(1).get_Location().get_Longitude())
        current_wp_advers = (stateMap.get(2).get_Location().get_Latitude(), stateMap.get(2).get_Location().get_Longitude())

finally:
    print("closing socket")
    sock.close()
