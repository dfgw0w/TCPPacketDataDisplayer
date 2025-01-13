import struct
from time import sleep
import config, packetData
import re
import numpy as np
import playerFilter

#print(interestedHexList)

def findPos(startBit, data):
    posXBytes = data[startBit + packetData.POS_PACKET["PosStart"]: startBit + packetData.POS_PACKET["PosStart"] + 8]
    posYBytes = data[startBit + packetData.POS_PACKET["PosStart"] + 8: startBit + packetData.POS_PACKET["PosStart"] + 16]
    posZBytes = data[startBit + packetData.POS_PACKET["PosStart"] + 16: startBit + packetData.POS_PACKET["PosStart"] + 24]

    posXYZBytes = posXBytes + posYBytes + posZBytes

    X, Y, Z = 9999999999, 9999999999, 9999999999

    if len(posXYZBytes) == 24:
        X, Y, Z = struct.unpack("lll", bytearray.fromhex(posXYZBytes)[0:4 * 3])
    else:
        print("Bugged position packet: " + data)

    return X,Y,Z

def decodeName(data):
    try:
        return bytes.fromhex(data).decode("ascii")
    except:
        print("Can't decode name")
        print(data)
        return "Failed to decode"

def parse(data, packetFrom):
    hexLength = str(len(data))

    byte_string = bytes.fromhex(data)
    ascii_string = byte_string.decode("ASCII", errors="ignore")

    interestedAscii = ["Satchel", "Pickables"]

    for target in interestedAscii:
        if target in ascii_string:
            print("[" + target + "] [Length]: " + hexLength + ", " + data + "\n")

    #if packetData.UNLOAD_PACKET["Unload"] in data:
    #    print("[Unload] [Length]: " + hexLength + ", " + data + "\n")

    """
    if config.PLAYER_FILTER:
        for playerID in playerFilter.PLAYERLIST:
            if data.find(playerID) != -1:
                return None
    """

    #berham = data.find("0de46b00") != -1
    #ottalia = data.find("fecff770") != -1
    #pippidoog = data.find("529fe87a") != -1
    #mikebigfish = data.find("c7d6c4b9") != -1
    #mikefish = data.find("d6fbab04") != -1
    #bigblack = data.find("a8ff2e33") != -1
    #bear = data.find("6cd1") != -1

    #target =
    """
    if berham:
        print("", end="")
        if hexLength != "86":
            print("[berham] [Length]: " + hexLength + ", " + data + "\n")
    elif ottalia:
        print("", end="")
        if hexLength != "86":
            print("[ottalia] [Length]: " + hexLength + ", " + data + "\n")
    else:
        print("", end="")
        #return None
    """
    # Future me please refactor fish
    if config.mode == "fish":

        if hexLength == str(packetData.FISH_SHAKE_PACKET["length"]):
            interestedByte = data[packetData.FISH_SHAKE_PACKET["interested"]]
            if interestedByte == str(packetData.FISH_SHAKE_PACKET["bite"]):
                return "pull"
            elif interestedByte == str(packetData.FISH_SHAKE_PACKET["bottom"]):
                sleep(1)
                return "bottom"
        elif hexLength == str(packetData.FISH_SWIM_PACKET["length"]):
            if data[packetData.FISH_SWIM_PACKET["interested"]] == str(packetData.FISH_SWIM_PACKET["swim"]):
                return "release"
            elif data[packetData.FISH_SWIM_PACKET["interested"]] == str(packetData.FISH_SWIM_PACKET["tired"]):
                return "pull"

    # 0 = playerID, 1 = action, 2~? = data

    if config.mode == "parry":
        print("", end = "")

        # Position
        posBit = data.find(packetData.POS_PACKET["Signature"])
        if posBit != -1:

            playerID = data[posBit + packetData.POS_PACKET["PlayerIdStart"]:
                            posBit + packetData.POS_PACKET["PlayerIdEnd"]]

            X, Y, Z = findPos(posBit, data)

            if config.DEBUG_SELF_ID:
                X, Y, Z = findPos(posBit, data)
                #print("Your Possible Position and ID: X: " +
                #      str(X) + ", Y: " + str(Y) + ", Z: " + str(Z) + ", ID: " + str(playerID))
                #print("Your Transform Packet: " + data)

            return playerID, "pos", X, Y, Z

        # Direction
        blockStartBit = data.find(packetData.DIRECTION_PACKET["Signature"])

        if blockStartBit != -1:
            if any(c in data[blockStartBit + packetData.blockBit] for c in ['c', 'e', 'd', 'f']):
                playerId = data[blockStartBit + packetData.DIRECTION_PACKET["idStart"] :
                                blockStartBit + packetData.DIRECTION_PACKET["idEnd"]]
                print("Dir from player ID: " + playerId + ", dir: " + packetData.DIRECTION_PACKET[data[blockStartBit + packetData.blockBit]])
                return playerId, "dir", packetData.DIRECTION_PACKET[data[blockStartBit + packetData.blockBit]]

        # attack & feint & reset
        attackBit = data.find(packetData.ATTACK_FEINT_PACKET["Signature"])

        if attackBit != -1:
            if "0de46b00" in data:
                print("Attack from Berham: " + data)
            playerId = data[attackBit + packetData.ATTACK_FEINT_PACKET["PlayerIdStart"] : attackBit + packetData.ATTACK_FEINT_PACKET["PlayerIdEnd"]]
            if any(c in data[packetData.blockSignalBit + attackBit]
                   for c in packetData.ATTACK_FEINT_PACKET["blockSignal"]):
                print("Attack from player ID: " + playerId)
                return playerId, "atkAction", "block"
            if any(c in data[packetData.blockSignalBit + attackBit]
                   for c in packetData.ATTACK_FEINT_PACKET["resetSignal"]):
                print("Reset/Feint from player ID: " + playerId)
                return playerId, "atkAction", "reset"

        # Load Info
        """
        loadMob = data.find(packetData.LOAD_PACKET["Load"])
        if loadMob != -1:

            # Load player at the same packet

            #if data.find(packetData.PLAYER_DATA_PACKET["Guild"]) != -1:
                #print("!!!!!!!!! Loaded with player")

            # unload player at the same packet

            unloadPlayer = data.find(packetData.UNLOAD_PACKET["Unload"])
            if unloadPlayer != -1:
                print("[LoadMob] !!!!!!!!! UnLoaded with player")

            x = re.finditer("00001b000000", data)

            loadIndex = []
            loadData = []

            for occurrence in x:
                loadIndex.append([occurrence.start(), data[occurrence.start() + 12: occurrence.start() + 14]])

            for x in range(len(loadIndex)):
                slice = ""
                if x + 1 < len(loadIndex):
                    slice = data[loadIndex[x][0]:loadIndex[x + 1][0]]
                else:
                    slice = data[loadIndex[x][0]:]

                idStartIndex = slice.find("00750000001b")

                nameStartIndex = loadIndex[x][0] + 16
                nameByteString = bytes.fromhex(data[nameStartIndex: nameStartIndex + int(loadIndex[x][1], 16) * 2])
                ascii_string = nameByteString.decode("ASCII", errors="ignore")

                loadData.append([slice[idStartIndex + 20: idStartIndex + 28], ascii_string])

            for mobData in loadData:
                print("Loaded modID: " + mobData[0] + ", Name: " + ascii_string)
                if ascii_string == "" or ascii_string == None:
                    print("[wrong loading] [Length]: " + hexLength + ", " + data + "\n")


            return "loadMob", "loadMob", loadData
        """

        # Player info
        playerSpawn = data.find(packetData.PLAYER_DATA_PACKET["Guild"])
        if playerSpawn != -1:

            x = re.finditer(packetData.PLAYER_DATA_PACKET["Guild"], data)

            playerDataSlice = []
            playerDataIndex = []
            playerInfoList = []

            for occurrence in x:
                playerDataIndex.append(occurrence.start())

            for x in range(len(playerDataIndex)):
                slice = ""
                if x + 1 < len(playerDataIndex):
                    slice = data[playerDataIndex[x]:playerDataIndex[x + 1] - 1]
                else:
                    slice = data[playerDataIndex[x]:]

                playerDataSlice.append(slice)

            for slice in playerDataSlice:
                playerGuild = ""
                playerGuildWordCount = int(slice[9], 16)

                if playerGuildWordCount != 0:
                    playerGuildHexString = slice[12: 12 + playerGuildWordCount * 2]
                    playerGuild = decodeName(playerGuildHexString)
                else:
                    playerGuild = "No Guild"

                nameStartIndex = slice.find(packetData.PLAYER_DATA_PACKET["Name"])
                playerNameCount = int(slice[nameStartIndex + 9], 16)
                playerNameHexString = slice[nameStartIndex + 12: nameStartIndex + 12 + playerNameCount * 2]
                playerName = decodeName(playerNameHexString)

                idStartIndex = slice.find(packetData.PLAYER_DATA_PACKET["ID"])
                playerID = slice[idStartIndex + 24: idStartIndex + 32]

                playerInfo = [playerID, playerName, playerGuild]
                playerInfoList.append(playerInfo)

                print("Might be player spawn signature, Name: " + playerName + ", Guild: " + playerGuild + ", ID: " + playerID + ".\n")

            return "info", "info", playerInfoList

        # Unload Packet

        unloadPlayer = data.find(packetData.UNLOAD_PACKET["Unload"])
        if unloadPlayer != -1:

            if data.find(packetData.LOAD_PACKET["Load"]) != -1:
                print("[Unload Player] !!!!!!!!! Loaded with mob")

            if data.find(packetData.PLAYER_DATA_PACKET["Guild"]) != -1:
                print("[Unload Player] !!!!!!!!! Loaded with player")

            x = re.finditer(packetData.UNLOAD_PACKET["Unload"], data)

            unloadIndex = []
            unloadList = []

            for occurrence in x:
                unloadIndex.append(occurrence.start())

            for unloadByte in unloadIndex:
                unloadList.append(data[unloadByte + 22: unloadByte + 30])

            return "unload", "unload", unloadList


    #if packetFrom == "From server" and hexLength != "24":
    #    print("[" + packetFrom + "] [Length]: " + hexLength + ", " + data + "\n")
    #elif packetFrom == "From local" and hexLength != "24":
    #    print("[" + packetFrom + "] [Length]: " + hexLength + ", " + data + "\n")

    return None