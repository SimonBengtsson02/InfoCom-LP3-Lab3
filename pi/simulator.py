import math
import requests
import argparse

from sense_hat import SenseHat
import pygame
sense = SenseHat()

def getMovement(src, dst):

    speed = 0.00002
    dst_x, dst_y = dst
    x, y = src
    direction = math.sqrt((dst_x - x)**2 + (dst_y - y)**2)
    longitude_move = speed * ((dst_x - x) / direction )
    latitude_move = speed * ((dst_y - y) / direction )
    return longitude_move, latitude_move

def moveDrone(src, d_long, d_la):
    x, y = src
    x = x + d_long
    y = y + d_la        
    return (x, y)

def send_location(SERVER_URL, id, drone_coords, status):
    if(status == 'idle'):
        sense.show_letter("I", (0,255,0))
    elif(status == 'busy'):
        sense.show_letter("B", (255,0,0))
    elif(status == 'waiting'):
        sense.show_letter("W", (255,230,30))

    with requests.Session() as session:
        drone_info = {'id': id,
                      'longitude': drone_coords[0],
                      'latitude': drone_coords[1],
                       'status': status
                    }
        resp = session.post(SERVER_URL, json=drone_info)

def distance(_fr, _to):
    _dist = ((_to[0] - _fr[0])**2 + (_to[1] - _fr[1])**2)*10**6
    return _dist

def run(id, current_coords, from_coords, to_coords, SERVER_URL):
    drone_coords = current_coords

    pygame.mixer.music.load("space-odyssey.mp3")
    pygame.mixer.music.play()

    d_long, d_la =  getMovement(drone_coords, from_coords)
    while ((from_coords[0] - drone_coords[0])**2 + (from_coords[1] - drone_coords[1])**2)*10**6 > 0.0002:
        drone_coords = moveDrone(drone_coords, d_long, d_la)
        send_location(SERVER_URL, id=id, drone_coords=drone_coords, status='busy')
        with requests.Session() as session:
            drone_info = {'id': id,
                          'longitude': drone_coords[0],
                          'latitude': drone_coords[1],
                          'status': 'busy'
                        }
            resp = session.post(SERVER_URL, json=drone_info)
    d_long, d_la =  getMovement(drone_coords, to_coords)

    send_location(SERVER_URL, id=id, drone_coords=drone_coords, status='waiting')

    pygame.mixer.music.stop()
    doorbell = pygame.mixer.Sound("doorbell-1.wav")
    doorbell.play()

    loop = True
    while(loop):
        for event in sense.stick.get_events():
            print(event.action)
            if event.action == "pressed" and event.direction == "up":
                loop = False
    
    pygame.mixer.music.load("space-odyssey.mp3")
    pygame.mixer.music.play()

    while ((to_coords[0] - drone_coords[0])**2 + (to_coords[1] - drone_coords[1])**2)*10**6 > 0.0002:
        drone_coords = moveDrone(drone_coords, d_long, d_la)
        send_location(SERVER_URL, id=id, drone_coords=drone_coords, status='busy')
        with requests.Session() as session:
            drone_info = {'id': id,
                          'longitude': drone_coords[0],
                          'latitude': drone_coords[1],
                          'status': 'busy'
                        }
            resp = session.post(SERVER_URL, json=drone_info)
    with requests.Session() as session:
            drone_info = {'id': id,
                          'longitude': drone_coords[0],
                          'latitude': drone_coords[1],
                          'status': 'idle'
                         }
            resp = session.post(SERVER_URL, json=drone_info)
    with open('coords.txt', 'w') as file:
        file.write(str(drone_coords[0]) + '\n')
        file.write(str(drone_coords[1]) + '\n')

    send_location(SERVER_URL, id=id, drone_coords=drone_coords, status='idle')

    pygame.mixer.music.stop()
    doorbell.play()

    return drone_coords[0], drone_coords[1]
   
if __name__ == "__main__":

    pygame.mixer.init()
    coin = pygame.mixer.Sound("coin.wav")
    coin.play()

    # Fill in the IP address of server, in order to location of the drone to the SERVER
    #===================================================================
    SERVER_URL = "http://192.168.1.1:5001/drone"
    #===================================================================

    parser = argparse.ArgumentParser()
    parser.add_argument("--clong", help='current longitude of drone location' ,type=float)
    parser.add_argument("--clat", help='current latitude of drone location',type=float)
    parser.add_argument("--flong", help='longitude of input [from address]',type=float)
    parser.add_argument("--flat", help='latitude of input [from address]' ,type=float)
    parser.add_argument("--tlong", help ='longitude of input [to address]' ,type=float)
    parser.add_argument("--tlat", help ='latitude of input [to address]' ,type=float)
    parser.add_argument("--id", help ='drones ID' ,type=str)
    args = parser.parse_args()
    print(args.clong)
    current_coords = (args.clong, args.clat)
    from_coords = (args.flong, args.flat)
    to_coords = (args.tlong, args.tlat)

    print(current_coords, from_coords, to_coords)
    drone_long, drone_lat = run(args.id ,current_coords, from_coords, to_coords, SERVER_URL)
    # drone_long and drone_lat is the final location when drlivery is completed, find a way save the value, and use it for the initial coordinates of next delivery
    #=============================================================================
    