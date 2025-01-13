# Network Settings

# For detect own IP
IP_LIST_TO_SERVER = [
    "xxx.xxx.xxx.xxx"   # Server IP
]

# For all other packet
IP_TO_LOCAL = "192.168.1.196"  # SERVER_TO_LOCAL, use for find self position
                                # Start with 192.168.x.xxx

PORT_LIST = [
    3724,           # game's ip port
    2266,
    12729
    #11516
    #15299,
    #31031,
    #17111           # item database port
]

NIC = "Software Loopback Interface 1"       # Use this if you are using a VPN
#Software Loopback Interface 1
#"Intel(R) Ethernet Controller (3) I225-V"  # Otherwise own NIC

port_filter_string = "port "
for port in PORT_LIST:
    port_filter_string += str(port) + " or port "
port_filter_string = port_filter_string[:-9]

IP_List = IP_LIST_TO_SERVER
IP_List.append(IP_TO_LOCAL)

# Packet Settings

SELF_ID = [
    "xxxxxxxx",     # own character ID #1
    "yyyyyyyy",     # own character ID #2
    "zzzzzzzz"      # own character ID #3
]

# Mode

mode = "parry"      # Legacy code
PLAYER_FILTER = True
DEBUG_SELF_ID = False
EXIT_LAG = True

# Dev

DEBUG_LOCAL_TO_SERVER = False
WRITE_LOG = False

# Overlay

overlay_playerToShow = 2

overlay_xOffset = 850
overlay_yOffset = 30

overlay_width = 600
overlay_height = 650

dirIndicatorSize = 20
dirIndicatorColor = "#9C9C9C"

atkIndicatorSize = 20
atkIndicatorColor = "#8cff00"

DISPLAY_PLAYER_DISTANCE = 10
DISPLAY_CLEAR_DELAY = 0.8