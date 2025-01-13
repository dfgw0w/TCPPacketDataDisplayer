import glob
import time
import tkinter as tk
from PIL import ImageTk
from threading import Thread, Event
from ctypes import windll

import config
import playerFilter
import utils


#←↑→↓

class Overlay(Thread):

    def __init__(self):
        super().__init__()

        self.radarObjectDict = {}
        self.playerInfoDict = {}
        self.radarDebugDict = {}
        self.radarObjectSize = 7

        self.radarUpdateRate = 100

        self.isDisplayDistance = True
        self.isDisplayHeight = False
        self.isDisplayGuild = True

        self.initializeWindow()

        #self.radarWindow.config(highlightbackground='#000000')
        #self.radarWindow.tk_setPalette("beige")
        #self.radarWindow.overrideredirect(True)
        #self.radarWindow.wm_attributes('-transparentcolor', 'beige')
        #self.radarWindow.wm_attributes('-topmost', True)
        #self.radarWindow.attributes('-alpha', 0.3)

        self.playersAttackInfo = []

        for x in range(config.overlay_playerToShow):
            dirPackFrame = tk.Frame(self.dirWindow,
                                         #bg="blue"
                                         )
            dirPackFrame.pack(fill="x")

            playersNameStringVar = tk.StringVar()
            playersNameStringVar.set("")

            playersName = tk.Label(dirPackFrame, fg="orange",
                                        font=("Verdana", config.dirIndicatorSize), anchor="e",
                                        width=20, height=1,
                                        #bg="black",
                                        textvariable=playersNameStringVar,
                                        justify="right")

            playersName.pack(expand="1", fill="x", side="left")

            dirStringVar = tk.StringVar()
            dirStringVar.set("")

            dirLabel = tk.Label(dirPackFrame, fg=config.dirIndicatorColor,
                                     font=("Verdana", config.dirIndicatorSize * 4),
                                     # width=25, height=1,
                                     #bg="black",
                                     textvariable=dirStringVar,
                                     justify="right")
            dirLabel.pack(expand="1", fill="x", side="left")

            self.playersAttackInfo.append([playersNameStringVar, dirStringVar, dirLabel])



        self.updateRadar()

        self.indicatorAttackStartTime = [[-999, 0], [-999, 0]]
        self.indicatorAttackEndTime = -999
        self.updateIndicator()

    def run(self):
        self.window.mainloop()

    def join(self, timeout=None):
        super().join(timeout)

    def displayDirection(self, overlayPlayerParryList):
        #print("overlay command: " + command)
        for i in range(len(overlayPlayerParryList)):

            playerNameString = overlayPlayerParryList[i][1]
            command = overlayPlayerParryList[i][2]
            isAttack = overlayPlayerParryList[i][3]

            #print("Set command: " + command)
            #print("Set isAttack: " + str(isAttack))
            self.playersAttackInfo[i][0].set(playerNameString)
            dir = "Not Set"

            if command == "top":
                dir = "↑"
            elif command == "right":
                dir = "←"
            elif command == "left":
                dir = "→"
            elif command == "down":
                dir = "↓"
            elif command == "reset":
                dir = ""

            if dir != "Not Set":
                self.playersAttackInfo[i][1].set(dir)
                self.playersAttackInfo[i][2].configure(fg=config.dirIndicatorColor)
                #self.clearAtkOverlay(i)
            if isAttack:
                if dir == "Not Set":
                    print("No dir but attacked, bug")
                    #self.playersAttackInfo[i][2].set("bug")
                else:
                    #self.playersAttackInfo[i][2].set(dir)
                    self.playersAttackInfo[i][2].configure(fg=config.atkIndicatorColor)
                    #self.window.after(500, self.clearAtkOverlay(i))
                    #self.indicatorAttackStartTime[i][0] = time.time()
                    #self.indicatorAttackStartTime[i][1] = i


    def clearAtkOverlay(self, index):
        self.playersAttackInfo[index][2].set("")

    def getRadarDebugText(self, playerID, radaData):
        debugText = "Player Dict key count: " + str(radaData)
        return debugText

    def updatePosDebug(self, playerID, radarData):

        debugText = self.getRadarDebugText(playerID, radarData)

        if playerID not in self.radarDebugDict:
            canvasTextObject = self.radarCanvas.create_text(10, 10 + 15 * len(self.radarDebugDict),
                                                            text=str(debugText), anchor="w")
            tempDict = {playerID: canvasTextObject}
            self.radarDebugDict.update(tempDict)
        else:
            self.radarCanvas.itemconfigure(self.radarDebugDict[playerID], text=str(debugText))

    def getRadarRect(self, radarRect):
        x0 = (radarRect[0] - self.radarObjectSize / 2 + 400)
        x1 = (radarRect[0] + self.radarObjectSize / 2 + 400)
        y0 = (radarRect[1] - self.radarObjectSize / 2 + 400)
        y1 = (radarRect[1] + self.radarObjectSize / 2 + 400)

        return x0, x1, y0, y1

    def getRadarObjectText(self, playerID, radarData):
        text = ""
        heightOffset = 10
        if playerID in playerFilter.PLAYERLIST:
            text += playerFilter.PLAYERLIST[playerID]
        else:
            if radarData[3] != "":
                text += radarData[3]
            else:
                text += str(playerID)

        if self.isDisplayDistance:
            text += "\nD: " + str(round(radarData[1], 1)) + "m"
            heightOffset += 10

        if self.isDisplayHeight:
            text += "\nH: " + str(round(radarData[2], 1)) + "m"
            heightOffset += 10

        if self.isDisplayGuild:
            if radarData[4] != "" and radarData[4] != "No Guild":
                text += "\nGuild: " + radarData[4]
                heightOffset += 10

        return text, heightOffset

    def setPlayerInfo(self, playerID, radarData, keyToDelete):

        if playerID not in self.radarObjectDict:

            canvasIconObject = ""
            canvasTextObject = ""

            radarText, heightOffset = self.getRadarObjectText(playerID, radarData)

            if playerID in playerFilter.PLAYERLIST or "Indomie" in radarText:
                canvasIconObject = self.radarCanvas.create_rectangle(0, 0, 7, 7, fill='green')
                canvasTextObject = self.radarCanvas.create_text(400, 400, fill="cyan", text=radarText)
            elif any(ally in radarText for ally in playerFilter.ALLIESLIST):
                canvasIconObject = self.radarCanvas.create_rectangle(0, 0, 7, 7, fill='white')
                canvasTextObject = self.radarCanvas.create_text(400, 400, fill="cyan", text=radarText)
            else:
                canvasIconObject = self.radarCanvas.create_rectangle(0, 0, 7, 7, fill='red')
                canvasTextObject = self.radarCanvas.create_text(400, 400, fill="white", text=radarText)

            x0, x1, y0, y1 = self.getRadarRect(radarData[0])

            self.radarCanvas.coords(canvasIconObject, x0, y0, x1, y1)
            self.radarCanvas.coords(canvasTextObject, x1 - self.radarObjectSize / 2, y1 - self.radarObjectSize / 2 + 10)

            tempDict = {playerID: [canvasIconObject, canvasTextObject, radarData]}
            self.radarObjectDict.update(tempDict)

            for friendsID in playerFilter.PLAYERLIST:
                if friendsID in self.radarObjectDict:
                    self.radarCanvas.tag_raise(self.radarObjectDict[friendsID][0])
                    self.radarCanvas.tag_raise(self.radarObjectDict[friendsID][1])

        else:
            tempDict = {playerID: [
                self.radarObjectDict[playerID][0],
                self.radarObjectDict[playerID][1],
                radarData]}
            self.radarObjectDict.update(tempDict)

        for key in keyToDelete:
            if key not in self.radarObjectDict:
                return
            self.radarCanvas.delete(self.radarObjectDict[key][0])
            self.radarCanvas.delete(self.radarObjectDict[key][1])

            del self.radarObjectDict[key]

    def updateRadar(self):

        for playerInfo in list(self.radarObjectDict.items()):

            radarData = playerInfo[1][2]

            x0, x1, y0, y1 = self.getRadarRect(radarData[0])

            self.radarCanvas.coords(playerInfo[1][0], x0, y0, x1, y1)

            radarText, heightOffset = self.getRadarObjectText(playerInfo[0], radarData)

            self.radarCanvas.itemconfigure(playerInfo[1][1], text = radarText)

            self.radarCanvas.coords(playerInfo[1][1], x1 - self.radarObjectSize / 2, y1 - self.radarObjectSize / 2 + heightOffset)

        self.window.after(self.radarUpdateRate, self.updateRadar)

    def initializeWindow(self):
        self.window = tk.Tk()
        self.window.geometry("1x1+" + "0" + "+" + "0")
        self.window.config(highlightbackground='#000000')
        self.window.tk_setPalette("beige")
        self.window.overrideredirect(True)
        self.window.wm_attributes('-transparentcolor', 'beige')
        self.window.wm_attributes('-topmost', True)

        extraNameSpace = config.overlay_width/3
        overlayGeoString = (str(int(config.overlay_width + extraNameSpace)) + "x" + str(config.overlay_height) + "+"
                         + str(int(utils.screensize[0] / 2 - config.overlay_width / 2 - extraNameSpace)) + "+"
                         + str(int(utils.screensize[1] / 2 - config.overlay_height / 2)))

        print(overlayGeoString)

        self.atkWindow = tk.Toplevel()
        self.atkWindow.geometry(overlayGeoString)
        self.atkWindow.config(highlightbackground='#000000')
        self.atkWindow.tk_setPalette("beige")
        self.atkWindow.overrideredirect(True)
        self.atkWindow.wm_attributes('-transparentcolor', 'beige')
        self.atkWindow.wm_attributes('-topmost', True)

        self.dirWindow = tk.Toplevel()
        self.dirWindow.geometry(overlayGeoString)
        self.dirWindow.config(highlightbackground='#000000')
        self.dirWindow.tk_setPalette("beige")
        self.dirWindow.overrideredirect(True)
        self.dirWindow.wm_attributes('-transparentcolor', 'beige')
        self.dirWindow.wm_attributes('-topmost', True)

        self.radarWindow = tk.Toplevel()
        self.radarWindow.geometry("800x800")
        self.radarCanvas = tk.Canvas(self.radarWindow, bg="grey", width=800, height=800)

        """
        self.debugWindow = tk.Toplevel()
        self.debugWindow.geometry("1920x1080")
        self.debugWindow.configure(background="grey")

        self.debugStringVar = tk.StringVar()
        self.debugStringVar.set("123")

        debugString = tk.Label(self.debugWindow, fg="black",
                               font=("Verdana", config.dirIndicatorSize), anchor="nw",
                               bg="grey",
                               textvariable=self.debugStringVar,
                               justify="right")

        debugString.grid()

        self.debugListedPlayer = tk.StringVar()
        self.debugListedPlayer.set("123")

        debugListedPlayer = tk.Label(self.debugWindow, fg="black",
                               font=("Verdana", config.dirIndicatorSize), anchor="nw",
                               bg="grey",
                               textvariable=self.debugListedPlayer,
                               justify="right")

        debugListedPlayer.grid(column=1, row=0)
        """

        self.radarCanvas.pack()

        self.photoimage = ImageTk.PhotoImage(file="RadarMap.png")
        self.radarCanvas.create_image(0, 0, image=self.photoimage, anchor="nw")

    def updateIndicator(self):
        for indicatorAttackStartTimeElement in self.indicatorAttackStartTime:
            if indicatorAttackStartTimeElement[0] != -999:
                if (self.indicatorAttackEndTime - indicatorAttackStartTimeElement[0]) > config.DISPLAY_CLEAR_DELAY:
                    self.clearAtkOverlay(indicatorAttackStartTimeElement[1])

            self.indicatorAttackEndTime = time.time()

        self.window.after(self.radarUpdateRate, self.updateIndicator)

    def updateDebugString(self, playerStatusDict, playerSortedList):
        debugString = ""
        for key in playerStatusDict:
            debugString += ("[" + str(key) + "] Distance: " + str(round(playerStatusDict[key][0], 1)) +
                           ", Dir: " + str(playerStatusDict[key][1]) +
                           ", Atk Action: " + str(playerStatusDict[key][2]) + "\n")

        debugSortedListString = ""
        for item in playerSortedList:
            debugSortedListString += ("[" + str(item[0]) + "] Distance: " + str(round(item[1][0], 1)) +
                           ", Dir: " + str(item[1][1]) +
                           ", Atk Action: " + str(item[1][2]) + "\n")

        self.debugStringVar.set(debugString)
        self.debugListedPlayer.set(debugSortedListString)