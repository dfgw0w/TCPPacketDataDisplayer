import config
import glob

FFISH_SHAKE_PACKET ={
    "length": 74,
    "interested": 39,
    "bite": 7,
    "bottom": "c"
}

FISH_SWIM_PACKET ={
    "length": 130,
    "interested": 95,
    "swim": 9,
    "tired": 'a'
}

DIRECTION_PACKET ={
    "c": "right",
    "d": "left",
    "e": "down",
    "f": "top",
    "id": "79457302",
    "idStart": 40,
    "idEnd": 48,

    "Signature": "260085210000008500efbeadde19f14e",
    "blockBit": 49
}

ATTACK_FEINT_PACKET = {
    "Signature": "1c0085170000008500efbeadde0ff187",

    "blockSignalBit": 57,
    "blockSignal": "89a",
    "resetSignal": "57",

    "PlayerIdStart": 40,
    "PlayerIdEnd": 48
}

POS_PACKET = {
    "Signature": "2900f186",
    "PosStart": 32,
    "PosEnd": 55,
    "PlayerIdStart": 16,
    "PlayerIdEnd": 24
}

PLAYER_DATA_PACKET = {
    "Guild": "11000900",
    "Name": "00006600",
    "ID": "0000810000001100",
}

UNLOAD_PACKET = {
    "Unload": "00efbeadde0ba6"
}

LOAD_PACKET = {
    "Load": "00001b000000",
    "ID": "00750000001b"
}

interestedPath = ""
blockBit = DIRECTION_PACKET["blockBit"]
blockSignalBit = ATTACK_FEINT_PACKET["blockSignalBit"]