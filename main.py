import numpy as np
from scapy.all import *

import packetParser as parser
from threading import Thread, Event

import playerFilter
import utils
from playerStatus import PlayerStatus
from time import time, sleep
import config
from overlayUI import Overlay

global timer
timer = time()

flags = {
    'F': 'FIN',
    'S': 'SYN',
    'R': 'RST',
    'P': 'PSH',
    'A': 'ACK',
    'U': 'URG',
    'E': 'ECE',
    'C': 'CWR'
}

def updateDictByList(original, id, data, dataIndex):

    tempDict = {id: [
        original[id][0],
        original[id][1],
        original[id][2],
        original[id][3],
        original[id][4],
        original[id][5]
    ]}

    tempDict[id][dataIndex] = data

    return tempDict

class Sniffer(Thread):

    def __init__(self):
        super().__init__()
        self.daemon = True
        self.stop_sniffer = Event()

        self.overlayPlayerParryList = []
        self.overlayLateUpdateDeleteList = []
        for x in range(config.overlay_playerToShow):
            self.overlayPlayerParryList.append(["", "", "", ""])

    def run(self):
        sniff(iface=config.NIC,
              prn=self.print_summary,
              filter=config.port_filter_string,
              stop_filter=self.should_stop_sniffer,
              store=False)

    def join(self, timeout=None):
        self.stop_sniffer.set()
        super().join(timeout)

    def should_stop_sniffer(self, packet):
        return self.stop_sniffer.is_set()

    def print_summary(self, pkt):

        if TCP not in pkt:
            print("", end="")  # do nothing
            #print("Bugged packet")
            return

        #print(type(pkt))

        if not pkt.haslayer(IP):
            print("", end="")  # do nothing
            print("Bugged packet")
            return

        if "U" in pkt['TCP'].flags:
            for i in range(10):
                print("urgent packet!!!!")

        if pkt['IP'].dst in config.IP_List and "P" in pkt['TCP'].flags:
            if Raw in pkt:
                load = pkt[Raw].load
                #hexdump(load)
                hex = load.hex()
                #print(hex)

                packetFrom = ""

                if pkt['IP'].dst == config.IP_TO_LOCAL:
                    packetFrom = "From server"
                    if config.DEBUG_SELF_ID:
                        return
                else:
                    packetFrom = "From local"

                if config.WRITE_LOG:
                    packetLog.writeLog(hex)

                result = parser.parse(hex, packetFrom)

                if result is not None:
                    # Maybe ignore mode here, use parser to filter mode
                    # refactor this feature me
                    if config.mode == "fish":
                        global timer
                        timer = time()

                        fishActionObject.doAction(result)

                    resultPlayerID = result[0]
                    resultAction = result[1]

                    # playerStatus, Key = playerID, value = [distance, dir, atkAction, [x, y], Name, Guild]

                    # Set empty value
                    if resultPlayerID not in playerStatusObject.othersStatus and resultPlayerID not in config.SELF_ID and resultPlayerID != "info":
                        tempDict = {resultPlayerID: [-9999, "", "", [9999, 9999, 9999], "", ""]}
                        playerStatusObject.othersStatus.update(tempDict)

                    # Set info
                    if resultAction == "info":

                        for playerInfo in result[2]:

                            #print("Player info recived: " + str(playerInfo))

                            if playerInfo[0] not in playerStatusObject.othersStatus and resultPlayerID not in config.SELF_ID:
                                tempDict = {playerInfo[0]: [-9999, "", "", [9999, 9999, 9999], "", ""]}
                                playerStatusObject.othersStatus.update(tempDict)

                            tempDict = updateDictByList(
                                playerStatusObject.othersStatus, playerInfo[0],
                                playerInfo[1],
                                4)

                            playerStatusObject.othersStatus.update(tempDict)

                            tempDict = updateDictByList(
                                playerStatusObject.othersStatus, playerInfo[0],
                                playerInfo[2],
                                5)

                            playerStatusObject.othersStatus.update(tempDict)

                    # Set pos
                    if resultAction == "pos":
                        if resultPlayerID in config.SELF_ID:
                            playerStatusObject.ownPos = np.array([result[2], result[3], result[4]])
                            playerStatusObject.ownPosXY = [result[2], result[3], result[4]]

                            # Update others Distance
                            for playerID in playerStatusObject.othersStatus:
                                tempDict = updateDictByList(
                                    playerStatusObject.othersStatus, playerID,
                                    playerStatusObject.getDistance(np.array(
                                        [playerStatusObject.othersStatus[playerID][3][0],
                                         playerStatusObject.othersStatus[playerID][3][1],
                                         playerStatusObject.othersStatus[playerID][3][2]]
                                    )),
                                    0)

                                playerStatusObject.othersStatus.update(tempDict)
                        else:
                            if resultPlayerID in playerStatusObject.othersStatus:

                                # Set Distance

                                tempDict = updateDictByList(
                                    playerStatusObject.othersStatus, resultPlayerID,
                                    playerStatusObject.getDistance(np.array([result[2], result[3], result[4]])),
                                    0)

                                playerStatusObject.othersStatus.update(tempDict)

                                # Set XY

                                tempDict = updateDictByList(
                                    playerStatusObject.othersStatus, resultPlayerID,
                                    [result[2], result[3], result[4]],
                                    3)

                                playerStatusObject.othersStatus.update(tempDict)

                    # Set dir
                    if resultAction == "dir":
                        if resultPlayerID in playerStatusObject.othersStatus:
                            tempDict = updateDictByList(playerStatusObject.othersStatus, resultPlayerID, result[2], 1)
                            playerStatusObject.othersStatus.update(tempDict)

                    # Set atkAction
                    if resultAction == "atkAction":

                        if resultPlayerID in playerStatusObject.othersStatus:
                            tempDict = updateDictByList(playerStatusObject.othersStatus, resultPlayerID, result[2], 2)
                            playerStatusObject.othersStatus.update(tempDict)

                    # List update for parry / indicator

                    listedStatus = list(playerStatusObject.othersStatus.items())

                    # overlay update

                    if len(listedStatus) != 0:

                        # radar

                        overlay.updatePosDebug("123", len(listedStatus))

                        for player in listedStatus:
                            if player[0] in config.SELF_ID:
                                continue

                            radarData = []

                            radarXY = [(player[1][3][0] - playerStatusObject.ownPosXY[0]) / 100000,
                                       (player[1][3][1] - playerStatusObject.ownPosXY[1]) / 100000]

                            radarData.append(radarXY)
                            radarData.append(player[1][0])
                            radarData.append((playerStatusObject.ownPosXY[2] - player[1][3][2]) / 100000)
                            radarData.append(player[1][4])
                            radarData.append(player[1][5])

                            overlay.setPlayerInfo(player[0], radarData, self.overlayLateUpdateDeleteList)


                        # Delete then sort for parry indicator
                        if config.PLAYER_FILTER:
                            selectedElement = []
                            for player in listedStatus:
                                if player[1][5] in playerFilter.ALLIESLIST:
                                    selectedElement.append(player)
                                elif player[0] in playerFilter.PLAYERLIST:
                                    selectedElement.append(player)
                                if player[1][0] == -9999:
                                    selectedElement.append(player)
                            for player in selectedElement:
                                if player in listedStatus:
                                    listedStatus.remove(player)

                        listedStatus.sort(key=lambda x: x[1][0])

                        # Dir
                        for x in range(config.overlay_playerToShow):
                            if x >= len(listedStatus):
                                continue
                            if listedStatus[x][1][0] > config.DISPLAY_PLAYER_DISTANCE:
                                for player in self.overlayPlayerParryList:
                                    if listedStatus[x][0] in player[0]:
                                        player[0] = ""
                                        player[1] = ""
                                        player[2] = ""
                                        player[3] = ""
                                continue
                            playerString = ""
                            isAttack = False
                            command = listedStatus[x][1][1]

                            playerString += str(round(listedStatus[x][1][0], 1)) + "m, "
                            if listedStatus[x][1][4] != "":
                                playerString += listedStatus[x][1][4]
                            else:
                                playerString += listedStatus[x][0]
                            playerString += ":"

                            if listedStatus[x][1][2] == "block":
                                if listedStatus[x][1][1] == "":
                                    print("Can't get dir packet from player " + listedStatus[x][1][4]
                                          + "for this attack")
                                #command = "block"
                                isAttack = True
                                #parryAction.doAction(listedStatus[x][1][1])
                            elif listedStatus[x][1][2] == "reset":
                                command = "reset"

                            self.overlayPlayerParryList[x][0] = listedStatus[x][0]
                            self.overlayPlayerParryList[x][1] = playerString
                            self.overlayPlayerParryList[x][2] = command
                            self.overlayPlayerParryList[x][3] = isAttack

                        #print(self.overlayPlayerParryList)
                        #utils.debug_data = self.overlayPlayerParryList
                        #utils.debug_name = "overlayPlayerParryList"
                        overlay.displayDirection(self.overlayPlayerParryList)

                        #overlay.updateDebugString(playerStatusObject.othersStatus, listedStatus)

                    utils.debug_data = playerStatusObject.ownPos
                    utils.debug_name = "Own Pos"
                    # Post dict update
                    keysToRemove = []

                    for playerID in playerStatusObject.othersStatus:
                        if playerStatusObject.othersStatus[playerID][2] == "block":
                            tempDict = updateDictByList(
                                playerStatusObject.othersStatus, playerID,
                                "", 2)

                            playerStatusObject.othersStatus.update(tempDict)

                            tempDict = updateDictByList(
                                playerStatusObject.othersStatus, playerID,
                                "", 1)

                            playerStatusObject.othersStatus.update(tempDict)

                        elif playerStatusObject.othersStatus[playerID][2] == "reset":
                            tempDict = updateDictByList(
                                playerStatusObject.othersStatus, playerID,
                                "", 2)

                            playerStatusObject.othersStatus.update(tempDict)

                            tempDict = updateDictByList(
                                playerStatusObject.othersStatus, playerID,
                                "", 1)

                            playerStatusObject.othersStatus.update(tempDict)

                    # Unload Packet
                    if resultAction == "unload":
                        for unloadID in result[2]:
                            if unloadID in playerStatusObject.othersStatus:
                                keysToRemove.append(unloadID)

                    for key in keysToRemove:
                        #print("delete key: " + key)
                        del playerStatusObject.othersStatus[key]

                    self.overlayLateUpdateDeleteList = keysToRemove

                #print(load)
                #print(pkt[Raw])


scapy.all.show_interfaces()

#wincap = BackgroundHandlerWin32('Mortal Online 2')

#fishActionObject = FishAction(wincap.img_hwnd.handle)
playerStatusObject = PlayerStatus()
#parryAction = ParryAction(wincap.img_hwnd.handle)

overlay = Overlay()
sniffer = Sniffer()
packetLog = ""
if config.WRITE_LOG:
    packetLog = PacketLogging()

print("Start sniffer thread")
sniffer.start()

overlay.run()


try:
    while True:

        # Legacy auto fishing, can replaced with a empty print
        key = cv2.waitKey(1)

        if config.mode == "fish":

            if time() - timer >= fishAction.FISH_TIMER:
                timer = time()
                fishActionObject.fish()

        if key == ord('q'):
            cv2.destroyAllWindows()

            print("[*] Stop sniffing")
            sniffer.join(2.0)

            if sniffer.is_alive():
                sniffer.socket.close()

            break

except KeyboardInterrupt:
    print("[*] Stop sniffing")
    sniffer.join(2.0)

    if sniffer.is_alive():
        sniffer.socket.close()
