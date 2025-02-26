from Tkinter import *
import tkFont
import tkFileDialog
from Exceptions import UserInputException
import os
import time
import re
import PmwFreeze as Pmw


import General
from DiffractionData import allExtensions


def removeTrailingCharacters(string,characterList):
    while string and string[-1] in characterList:
        string = string[0:-1]
    return string


def cleanstring(string):
    # remove beginning and ending newlines (and I think tabs and spaces)
    temp = string.strip()

    # remove any trailing colons or question marks
    temp = removeTrailingCharacters(temp,[':','?'])
    temp = temp.lower()
    return temp


def valueInListOfDict(list,key,value):
    for item in list:
        if item[key]==value:
            return 1
    return 0


class AbortDisplay:
    def __init__(self,master,abortFunc):
        self.main=Pmw.MegaToplevel(master)
        self.main.userdeletefunc(func=self.main.withdraw)
        self.main.title("ABORT")
        frame=Frame(self.main.interior(),width=50,height=50)
        frame.grid(row=1,column=1,padx=15,pady=15,sticky=N+E+S+W)

        self.button=Button(frame,text='ABORT', bg='red',fg='snow',
                width=6,height=2,font=tkFont.Font(size=40),command=abortFunc)
        self.button.grid(row=1,column=1,sticky=N+E+S+W)
        

class MacroMode:

    def abort(self):
        # sent a message to the running macro to abort
        self.CANCEL_FLAG = 1
        print 'ABORTING MACRO'


    def __init__(self,GUI,setstatus):
        """ Object to perform the macro recording/writing. 
            The object requires the GUI To work with. """

        self.GUI = GUI
        self.setstatus = setstatus

        # Create a list of all wigits in the GUI
        moveToCalibration = lambda GUI=self.GUI: GUI.xrdnb.selectpage('Calibration')
        moveToMasking = lambda GUI=self.GUI: GUI.xrdnb.selectpage('Masking')
        moveToCake = lambda GUI=self.GUI: GUI.xrdnb.selectpage('Cake')
        moveToIntegrate = lambda GUI=self.GUI: GUI.xrdnb.selectpage('Integrate')
        moveToMaindisp = lambda GUI=self.GUI: GUI.xrdnb.selectpage('Calibration')
        moveToCakedisp = lambda GUI=self.GUI: GUI.xrdnb.selectpage('Cake')
        moveToIntegratedisp = lambda GUI=self.GUI: GUI.xrdnb.selectpage('Integrate')

        self.allCheckBoxes = [
            {'name':'xc Fixed:','widget':self.GUI.centerX.cb,
                    'move to page':moveToCalibration,'var':self.GUI.centerX.fixedvar},
            {'name':'yc Fixed:','widget':self.GUI.centerY.cb,
                    'move to page':moveToCalibration,'var':self.GUI.centerY.fixedvar},
            {'name':'d Fixed:','widget':self.GUI.distance.cb,
                    'move to page':moveToCalibration,'var':self.GUI.distance.fixedvar},
            {'name':'E Fixed:','widget':self.GUI.energyOrWavelength.cb,
                    'move to page':moveToCalibration,
                    'var':self.GUI.energyOrWavelength.fixedvar},
            {'name':'lambda Fixed:','widget':self.GUI.energyOrWavelength.cb,
                    'move to page':moveToCalibration,
                    'var':self.GUI.energyOrWavelength.fixedvar},
            {'name':'alpha Fixed:','widget':self.GUI.alpha.cb,
                    'move to page':moveToCalibration,
                    'var':self.GUI.alpha.fixedvar},
            {'name':'beta Fixed:','widget':self.GUI.beta.cb,
                    'move to page':moveToCalibration,
                    'var':self.GUI.beta.fixedvar},
            {'name':'R Fixed:','widget':self.GUI.rotation.cb,
                    'move to page':moveToCalibration,
                    'var':self.GUI.rotation.fixedvar},
            {'name':'Draw Q Lines?','widget':self.GUI.drawQ.cb,
                    'move to page':moveToCalibration,
                    'var':self.GUI.drawQ.checkvar},
            {'name':'Draw dQ Lines?','widget':self.GUI.drawdQ.cb,
                    'move to page':moveToCalibration,
                    'var':self.GUI.drawdQ.checkvar},
            {'name':'Draw Peaks?','widget':self.GUI.drawPeaks.cb,
                    'move to page':moveToCalibration,
                    'var':self.GUI.drawPeaks.checkvar},
            {'name':'Use Old Peak List (if Possible)?',
                    'widget':self.GUI.useOldPeakListButton,
                    'move to page':moveToCalibration,
                    'var':self.GUI.useOldPeakList},
            {'name':'Do Greater Than Mask?','widget':self.GUI.doGreaterThanMask.cb,
                    'move to page':moveToMasking,
                    'var':self.GUI.doGreaterThanMask.checkvar},
            {'name':'Do Less Than Mask?', 'widget':self.GUI.doLessThanMask.cb,
                    'move to page':moveToMasking,
                    'var':self.GUI.doLessThanMask.checkvar},
            {'name':'Do Polygon Mask?', 'widget': self.GUI.doPolygonMask.cb,
                    'move to page':moveToMasking,
                    'var':self.GUI.doPolygonMask.checkvar},
            {'name':'Cake Do Polarization Correction?',
                    'widget':self.GUI.doPolarizationCorrectionCakeButton,
                    'move to page':moveToCake,
                    'var':self.GUI.doPolarizationCorrectionCake},
            {'name':'Constrain With Range On Right?',
                    'widget':self.GUI.constrainWithRangeOnRightButton,
                    'move to page':moveToIntegrate,
                    'var':self.GUI.constrainWithRangeOnRight},
            {'name':'Constrain With Range On Left?',
                    'widget':self.GUI.constrainWithRangeOnLeftButton,
                    'move to page':moveToIntegrate,
                    'var':self.GUI.constrainWithRangeOnLeft},
            {'name':'Integrate Do Polarization Correction?',
                    'widget':self.GUI.doPolarizationCorrectionIntegrateButton,
                    'move to page':moveToCake,
                    'var':self.GUI.doPolarizationCorrectionIntegrate},
		    {'name':'Diffraction Data Invert?',
                    'widget':self.GUI.maindisp.colinvert,
                    'move to page':moveToMaindisp,
                    'var':self.GUI.invertVarDiffraction},
		    {'name':'Diffraction Data Log Scale?',
                    'widget':self.GUI.maindisp.collog,
                    'move to page':moveToMaindisp,
                    'var':self.GUI.logVarDiffraction},
            {'name':'Diffraction Data Do Scale Factor?',
                    'widget':self.GUI.maindisp.doScaleFactor,
                    'move to page':moveToMaindisp,
                    'var':self.GUI.doScaleFactorVarDiffraction},
            {'name':'Diffraction Data Set Min/Max?',
                    'widget':self.GUI.maindisp.setMinMax,
                    'move to page':moveToMaindisp,
                    'var':self.GUI.setMinMaxVarDiffraction},
		    {'name':'Cake Data Invert?',
                    'widget':self.GUI.cakedisp.colinvert,
                    'move to page':moveToCakedisp,
                    'var':self.GUI.invertVarCake},
		    {'name':'Cake Data Log Scale?',
                    'widget':self.GUI.cakedisp.collog,
                    'move to page':moveToCakedisp,
                    'var':self.GUI.logVarCake}, 
            {'name':'Integration Data Log Scale?',
                    'widget':self.GUI.integratedisp.collog,
                    'move to page':moveToIntegratedisp,
                    'var':self.GUI.logVarIntegration},
            {'name':'Cake Data Do Scale Factor?',
                    'widget':self.GUI.cakedisp.doScaleFactor,
                    'move to page':moveToCakedisp,
                    'var':self.GUI.doScaleFactorVarCake},
            {'name':'Cake Data Set Min/Max?',
                    'widget':self.GUI.cakedisp.setMinMax,
                    'move to page':moveToMaindisp,
                    'var':self.GUI.setMinMaxVarCake},
        ]
        for widget in self.allCheckBoxes:
            widget['clean name'] = cleanstring(widget['name'])

        self.multipleDataFilesCommand = [
            {'name':'Multiple Data Files:','widget':self.GUI.fileentry,
                    'move to page':moveToCalibration,
                    'function':self.GUI.loadDiffractionFile},
        ]
        for widget in self.multipleDataFilesCommand:
            widget['clean name'] = cleanstring(widget['name'])

        self.dataFileCommand = [
            {'name':'Data File:','widget':self.GUI.fileentry,
                    'move to page':moveToCalibration,
                    'function':self.GUI.loadDiffractionFile},
        ]
        for widget in self.dataFileCommand:
            widget['clean name'] = cleanstring(widget['name'])

        self.allLoadEntryFieldsRequiringFilename = [
            {'name':'Q Data:','widget':self.GUI.qfileentry,
                    'move to page':moveToCalibration,
                    'function':self.GUI.selectQDataFile},
            {'name':'Default Folder:',
                    'widget':self.GUI.preferencesdisplay.defaultFolderEntry,
                    'function':self.GUI.setDefaultFolder},
        ]
        for widget in self.allLoadEntryFieldsRequiringFilename:
            widget['clean name'] = cleanstring(widget['name'])

        self.allEntryFieldsRequiringFloat = [
            {'name':'xc:','widget':self.GUI.centerX.ef,
                    'move to page':moveToCalibration},
            {'name':'yc:','widget':self.GUI.centerY.ef,
                    'move to page':moveToCalibration},
            {'name':'d:','widget':self.GUI.distance.ef,
                    'move to page':moveToCalibration},
            {'name':'E:','widget':self.GUI.energyOrWavelength.ef,
                    'move to page':moveToCalibration},
            {'name':'lambda:','widget':self.GUI.energyOrWavelength.ef,
                    'move to page':moveToCalibration},
            {'name':'alpha:','widget':self.GUI.alpha.ef,
                    'move to page':moveToCalibration},
            {'name':'beta:','widget':self.GUI.beta.ef,
                    'move to page':moveToCalibration},
            {'name':'R:','widget':self.GUI.rotation.ef,
                    'move to page':moveToCalibration},
            {'name':'pl:','widget':self.GUI.pixelLength.ef,
                    'move to page':moveToCalibration},
            {'name':'ph:','widget':self.GUI.pixelHeight.ef,
                    'move to page':moveToCalibration},
            {'name':'Stddev?','widget':self.GUI.stddev,
                    'move to page':moveToCalibration},
            {'name':"(Pixels Can't Be) Greater Than Mask:", 
                    'widget':self.GUI.greaterThanMask,
                    'move to page':moveToMasking},
            {'name':"(Pixels Can't Be) Less Than Mask:", 
                    'widget':self.GUI.lessThanMask,
                    'move to page':moveToMasking},
            {'name':'Cake Q Lower?',
                    'widget':self.GUI.qOrTwoThetaLowerCake,
                    'move to page':moveToCake},
            {'name':'Cake 2theta Lower?',
                    'widget':self.GUI.qOrTwoThetaLowerCake,
                    'move to page':moveToCake},
            {'name':'Cake Q Upper?',
                    'widget':self.GUI.qOrTwoThetaUpperCake,
                    'move to page':moveToCake},
            {'name':'Cake 2theta Upper?',
                    'widget':self.GUI.qOrTwoThetaUpperCake,
                    'move to page':moveToCake},
            {'name':'Cake Chi Lower?',
                    'widget':self.GUI.chiLowerCake,
                    'move to page':moveToCake},
            {'name':'Cake Chi Upper?',
                    'widget':self.GUI.chiUpperCake,
                    'move to page':moveToCake},
            {'name':'Cake P?',
                    'widget':self.GUI.PCake,
                    'move to page':moveToCake},
            {'name':'Integrate Q Lower?',
                    'widget':self.GUI.QOrTwoThetaLowerIntegrate,
                    'move to page':moveToIntegrate},
            {'name':'Integrate 2theta Lower?',
                    'widget':self.GUI.QOrTwoThetaLowerIntegrate,
                    'move to page':moveToIntegrate},
            {'name':'Integrate Q Upper?',
                    'widget':self.GUI.QOrTwoThetaUpperIntegrate,
                    'move to page':moveToIntegrate},
            {'name':'Integrate 2theta Upper?',
                    'widget':self.GUI.QOrTwoThetaUpperIntegrate,
                    'move to page':moveToIntegrate},
            {'name':'Integrate Chi Lower?',
                    'widget':self.GUI.chiLowerIntegrate,
                    'move to page':moveToIntegrate},
            {'name':'Integrate Chi Upper?',
                    'widget':self.GUI.chiUpperIntegrate,
                    'move to page':moveToIntegrate},
            {'name':'Integrate P?',
                    'widget':self.GUI.PIntegrate,
                    'move to page':moveToIntegrate},
            {'name':'Diffraction Data Scale Factor',
                    'widget':self.GUI.maindisp.scaleFactor,
                    'move to page':moveToMaindisp},
            {'name':'Diffraction Data Min Intensity',
                    'widget':self.GUI.maindisp.minIntensity,
                    'move to page':moveToMaindisp},
            {'name':'Diffraction Data Max Intensity',
                    'widget':self.GUI.maindisp.maxIntensity,
                    'move to page':moveToMaindisp},
            {'name':'Cake Data Scale Factor',
                    'widget':self.GUI.cakedisp.scaleFactor,
                    'move to page':moveToCakedisp},
            {'name':'Cake Data Min Intensity',
                    'widget':self.GUI.cakedisp.minIntensity,
                    'move to page':moveToCakedisp},
            {'name':'Cake Data Max Intensity',
                    'widget':self.GUI.cakedisp.maxIntensity,
                    'move to page':moveToCakedisp},
        ]
        for widget in self.allEntryFieldsRequiringFloat:
            widget['clean name'] = cleanstring(widget['name'])
				

        self.allEntryFieldsRequiringInt = [
            {'name':'Fit Number Of Chi?',
                    'widget':self.GUI.numberOfChiInput,
                    'move to page':moveToCalibration},
            {'name':'Cake Number Of Q?',
                    'widget':self.GUI.numQOrTwoThetaCake,
                    'move to page':moveToCake},
            {'name':'Cake Number Of 2theta?',
                    'widget':self.GUI.numQOrTwoThetaCake,
                    'move to page':moveToCake},
            {'name':'Cake Number Of Chi?',
                    'widget':self.GUI.numChiCake,
                    'move to page':moveToCake},
            {'name':'Integrate Number Of Q?',
                    'widget':self.GUI.numQOrTwoThetaIntegrate,
                    'move to page':moveToIntegrate},
            {'name':'Integrate Number Of 2theta?',
                    'widget':self.GUI.numQOrTwoThetaIntegrate,
                    'move to page':moveToIntegrate},
            {'name':'Integrate Number Of Chi?',
                    'widget':self.GUI.numChiIntegrate,
                    'move to page':moveToIntegrate},        ]
        for widget in self.allEntryFieldsRequiringInt:
            widget['clean name'] = cleanstring(widget['name'])


        self.allColorMaps = [
            {'name':'Diffraction Data Colormaps:',
                    'widget':self.GUI.maindisp.colmap,
                    'move to page':moveToMaindisp},
            {'name':'Cake Data Colormaps:',
                    'widget':self.GUI.cakedisp.colmap,
                    'move to page':moveToCakedisp},
        ]
        for widget in self.allColorMaps:
            widget['clean name'] = cleanstring(widget['name'])


        self.allSaveButtonsRequiringFilename = [
            {'name':'Save To File',
                    'widget':self.GUI.saveCalibrationButton,
                    'function':self.GUI.calibrationDataSave,
                    'move to page':moveToCalibration},
            {'name':'Save Last Fit',
                    'widget':self.GUI.saveLastFitButton,
                    'function':self.GUI.saveLastFit,
                    'move to page':moveToCalibration},
            {'name':'Make/Save Peak List',
                    'widget':self.GUI.makeSavePeakListButton,
                    'function':self.GUI.savePeakList,
                    'move to page':moveToCalibration},
            {'name':'Save Mask','widget':self.GUI.saveMask,
                    'function':self.GUI.savePolygonsToFile,
                    'move to page':moveToMasking},
            {'name':'Save Caked Image',
                    'widget':self.GUI.saveCakeImageButton,
                    'function':self.GUI.saveCakeImage,
                    'move to page':moveToCake},
            {'name':'Save Caked Data',
                    'widget':self.GUI.saveCakeDataButton,
                    'function':self.GUI.saveCakeData,
                    'move to page':moveToCake},
            {'name':'Save Integration Data',
                    'widget':self.GUI.saveIntegrationDataButton,
                    'function':self.GUI.saveIntegratedIntensity,
                    'move to page':moveToIntegrate},
        ]
        for widget in self.allSaveButtonsRequiringFilename:
            widget['clean name'] = cleanstring(widget['name'])
		
        self.allLoadButtonsRequiringFilename = [
            {'name':'Load From File','widget':self.GUI.loadFromFileButton,
                    'function':self.GUI.calibrationDataLoad,
                    'move to page':moveToCalibration},
            {'name':'Load Mask','widget':self.GUI.loadMask,
                    'function':self.GUI.loadPolygonsFromFile,
                    'move to page':moveToMasking},
        ]
        for widget in self.allLoadButtonsRequiringFilename:
            widget['clean name'] = cleanstring(widget['name'])
		
        self.allColorInputs = [
            {'name':'Draw Q Lines Color?',
                    'widget':self.GUI.drawQ.button,
                    'var':self.GUI.qLinesColor,
                    'function':self.GUI.getQColor,
                    'move to page':moveToCalibration},
            {'name':'Draw dQ Lines Color',
                    'widget':self.GUI.drawdQ.button,
                    'var':self.GUI.dQLinesColor,
                    'function':self.GUI.getdQColor,
                    'move to page':moveToCalibration},
            {'name':'Draw Peaks Color?',
                    'widget':self.GUI.drawPeaks.button,
                    'var':self.GUI.peakLinesColor,
                    'function':self.GUI.getPeaksColor,
                    'move to page':moveToCalibration},
            {'name':'Greater Than Mask Color?',
                    'widget':self.GUI.doGreaterThanMask.button,
                    'var':self.GUI.greaterThanMaskColor,
                    'function':self.GUI.getGreaterThanMaskColor,
                    'move to page':moveToMasking},
            {'name':'Less Than Mask Color?',
                    'widget':self.GUI.doLessThanMask.button,
                    'var':self.GUI.lessThanMaskColor,
                    'function':self.GUI.getLessThanMaskColor,
                    'move to page':moveToMasking},
            {'name':'Polygon Mask Color?',
                    'widget':self.GUI.doPolygonMask.button,
                    'var':self.GUI.polygonMaskColor,
                    'function':self.GUI.getPolygonMaskColor,
                    'move to page':moveToMasking}
        ]
        for widget in self.allColorInputs:
            widget['clean name'] = cleanstring(widget['name'])
		
        self.allOtherButtons = [
            {'name':'Get From Header',
                    'widget':self.GUI.getFromHeaderButton,
                    'function':self.GUI.calibrationDataFromHeader,
                    'move to page':moveToCalibration},
            {'name':'Previous Values',
                    'widget':self.GUI.previousValuesButton,
                    'function':self.GUI.calibrationDataUndo,
                    'move to page':moveToCalibration},
            {'name':'Update',
                    'widget':self.GUI.updateDiffractionImageButton,
                    'function':self.GUI.maindisp.updateimage,
                    'move to page':moveToCalibration},
            {'name':'Do Fit',
                    'widget':self.GUI.doFitButton,
                    'function':self.GUI.doFit,
                    'move to page':moveToCalibration},
            {'name':'Clear Mask',
                    'widget':self.GUI.clearMask,
                    'function':self.GUI.removePolygons,
                    'move to page':moveToMasking},
            {'name':'AutoCake',
                    'widget':self.GUI.autoCakeButton,
                    'function':self.GUI.autoCake,
                    'move to page':moveToCake},
            {'name':'Do Cake',
                    'widget':self.GUI.doCakeButton,
                    'function':self.GUI.cakedisp.updateimage,
                    'move to page':moveToCake},
            {'name':'Last Cake',
                    'widget':self.GUI.lastCakeButton,
                    'function':self.GUI.undoZoomCakeImage,
                    'move to page':moveToCake},
            {'name':'AutoIntegrate Q-I',
                    'widget':self.GUI.autoIntegrateQOrTwoThetaIButton,
                    'function':self.GUI.autoIntegrateQOrTwoThetaI,
                    'move to page':moveToIntegrate},
            {'name':'AutoIntegrate 2theta-I',
                    'widget':self.GUI.autoIntegrateQOrTwoThetaIButton,
                    'function':self.GUI.autoIntegrateQOrTwoThetaI,
                    'move to page':moveToIntegrate},
            {'name':'AutoIntegrate chi-I',
                    'widget':self.GUI.autoIntegrateChiIButton,
                    'function':self.GUI.autoIntegrateChiI,
                    'move to page':moveToIntegrate},
            {'name':'Integrate Q-I',
                    'widget':self.GUI.integrateQOrTwoThetaIButton,
                    'function':self.GUI.integrateQOrTwoThetaI,
                    'move to page':moveToIntegrate},
            {'name':'Integrate 2theta-I',
                    'widget':self.GUI.integrateQOrTwoThetaIButton,
                    'function':self.GUI.integrateQOrTwoThetaI,
                    'move to page':moveToIntegrate},
            {'name':'Integrate chi-I',
                    'widget':self.GUI.integrateChiIButton,
                    'function':self.GUI.integrateChiI,
                    'move to page':moveToIntegrate},
    	]
        for widget in self.allOtherButtons:
            widget['clean name'] = cleanstring(widget['name'])

		
        self.allScales = [
            {'name':'Diffraction Data low',
                    'widget':self.GUI.maindisp.intensitylo,
                    'move to page':moveToMaindisp},
            {'name':'Diffraction Data hi',
                    'widget':self.GUI.maindisp.intensityhi,
                    'move to page':moveToMaindisp},
            {'name':'Cake Data low',
                    'widget':self.GUI.cakedisp.intensitylo,
                    'move to page':moveToCakedisp},
            {'name':'Cake Data hi',
                    'widget':self.GUI.cakedisp.intensityhi,
                    'move to page':moveToCakedisp},
        ]
        for widget in self.allScales:
            widget['clean name'] = cleanstring(widget['name'])

        self.allSaveMenuItemsRequiringFilename = [
            {'name':'Save Diffraction Image',
                    'widget':self.GUI.saveDiffractionImageMenuItem,
                    'function':self.GUI.saveDiffractionImage,},
        ]
        for widget in self.allSaveMenuItemsRequiringFilename:
            widget['clean name'] = cleanstring(widget['name'])


        self.standardQMenuItem = [
            {'name':'Standard Q','function':lambda name,GUI=self.GUI:
                    self.GUI.selectQDataFile(GUI.standardQFolder+os.sep+name+'.dat'),
                    'move to page':moveToCalibration}
        ]
        for widget in self.standardQMenuItem:
            widget['clean name'] = cleanstring(widget['name'])

        self.allCheckBoxMenuItems = [
            {'name':'Work In eV','var':self.GUI.eVorLambda,
             'function':lambda GUI=self.GUI: GUI.changeEVorLambda("Work in eV")},
            {'name':'Work in Lambda','var':self.GUI.eVorLambda,
            'function':lambda GUI=self.GUI: GUI.changeEVorLambda("Work in Lambda")},
            {'name':'Work in 2theta','var':self.GUI.Qor2Theta,
             'function':lambda GUI=self.GUI: GUI.changeQor2Theta("Work in 2theta")},
            {'name':'Work in Q','var':self.GUI.Qor2Theta,
             'function':lambda GUI=self.GUI: GUI.changeQor2Theta("Work in Q")},
        ]
        for widget in self.allCheckBoxMenuItems:
            widget['clean name'] = cleanstring(widget['name'])
        
        # create the abort display
        self.abortDisplay = AbortDisplay(self.GUI.xrdwin,self.abort)
        self.abortDisplay.main.withdraw()

        self.CANCEL_FLAG = None


    def runMacro(self):
    
        filename = tkFileDialog.askopenfilename(
                filetypes=[ ('dat file','*.dat'), ("All files", "*"), ], 
                initialdir=self.GUI.defaultDir,
                title="Load Macro")

        if filename in ['',()]: return 
   
        self.runMacroFromFilename(filename,moveAround=1,
            VERBOSE=1,ALLOWABORT=1)
		

    def runMacroFromFilename(self,filename,
            moveAround,VERBOSE,ALLOWABORT):
        """ moveAround = whether to move around in the GUI while
            running through macro commands. """

        if VERBOSE: print 'Testing the validity of the macro file'
        self.testMacroValidity(filename)
        # an error is raised of the file is bad
        if VERBOSE: print 'Macro File is Good!'

        if ALLOWABORT: self.abortDisplay.main.show()
        else: self.abortDisplay.main.withdraw()
        if ALLOWABORT: self.abortDisplay.button.update()

        self.setstatus(self.GUI.macrostatus,'Running Macro')
        self.GUI.macrostatus.pack(side=RIGHT)
        macro = Macro(filename)

        if VERBOSE: print 'Running the Macro File'

        line = macro.next()

        self.CANCEL_FLAG = None

        # make it do all the right things
        # if not ALLOWABORT, CANCEL_FLAG can never
        # change from equaling NONE
        while line != None and self.CANCEL_FLAG == None:

            cleanline = cleanstring(line)

            if VERBOSE: print ' - current: ',line 

            for widget in self.multipleDataFilesCommand:
                if cleanline == widget['clean name']:
                    if moveAround: widget['move to page']()
                    if ALLOWABORT: self.abortDisplay.main.show()
                    if ALLOWABORT: self.abortDisplay.button.update()
                    list = macro.next()

                    # the macro line is of the form:
                    # [ file_one.mar3450 file_two.mar3450 ]o
                    # remove the brackets [] before giving
                    # the string to the program
                    if VERBOSE: print ' - current: ',list

                    pattern= r"""\[(.*?)\]"""
                    regexp= re.compile(pattern, re.DOTALL)
                    filenames = regexp.findall(list)[0]

                    widget['function'](filenames.strip())

            # deal w/ each type of GUI item separately
            for widget in self.allLoadEntryFieldsRequiringFilename+\
                    self.dataFileCommand:
                if cleanline == widget['clean name']:
                    if moveAround: widget['move to page']()
                    if ALLOWABORT: self.abortDisplay.main.show()
                    if ALLOWABORT: self.abortDisplay.button.update()
                    filename = macro.next()
                    if VERBOSE: print ' - current: ',filename 
                    # Set the filename
                    widget['function'](filename.strip())

            for widget in self.allLoadButtonsRequiringFilename:
                if cleanline == widget['clean name']:
                    if moveAround: widget['move to page']()
                    if ALLOWABORT: self.abortDisplay.main.show()
                    if ALLOWABORT: self.abortDisplay.button.update()
                    # get the filename
                    filename = macro.next()
                    if VERBOSE: print ' - current: ',filename 
                    # Call the associated function requiring the filename
                    widget['function'](filename.strip())

            for widget in self.allSaveButtonsRequiringFilename:
                if cleanline == widget['clean name']:
                    if moveAround: widget['move to page']()
                    if ALLOWABORT: self.abortDisplay.main.show()
                    if ALLOWABORT: self.abortDisplay.button.update()
                    # get the filename

                    filename = macro.next()

                    # create the folder the file is in (if it 
                    # doesn't exit).
                    General.createFolderForFile(filename.strip())
                    if VERBOSE: print ' - current: ',filename 
                    # Call the associated function requiring the filename
                    widget['function'](filename.strip())

            for widget in self.allOtherButtons:
                if cleanline == widget['clean name']:
                    if moveAround: widget['move to page']()
                    if ALLOWABORT: self.abortDisplay.main.show()
                    if ALLOWABORT: self.abortDisplay.button.update()

                    if widget['name'] in ['AutoIntegrate Q-I','Integrate Q-I']:
                        self.GUI.changeQor2Theta('Work in Q')
                    if widget['name'] in ['AutoIntegrate 2theta-I',
                            'Integrate 2theta-I']:
                        self.GUI.changeQor2Theta('Work in 2theta')

                    # Call the associated function
                    widget['function']()

            for widget in self.allCheckBoxes:
                if cleanline == widget['clean name']:
                    if moveAround: widget['move to page']()
                    if ALLOWABORT: self.abortDisplay.main.show()
                    if ALLOWABORT: self.abortDisplay.button.update()

                    if widget['name']=='E Fixed:':
                        self.GUI.changeEVorLambda('Work in eV')
                    if widget['name']=='lambda Fixed:':
                        self.GUI.changeEVorLambda('Work in Lambda')

                    value = macro.next()
                    if VERBOSE: print ' - current: ',value 
                    # Set the check box
                    clean = cleanstring(value.lower())
                    if clean=='select':
                        widget['widget'].select()
                    elif clean=='deselect':
                        widget['widget'].deselect()

            for widget in self.allEntryFieldsRequiringFloat+\
                    self.allEntryFieldsRequiringInt:
                if cleanline == widget['clean name']:
                    if moveAround: widget['move to page']()
                    if ALLOWABORT: self.abortDisplay.main.show()
                    if ALLOWABORT: self.abortDisplay.button.update()

                    if widget['name']=='E:':
                        self.GUI.changeEVorLambda('Work in eV')
                    if widget['name']=='lambda:':
                        self.GUI.changeEVorLambda('Work in Lambda')

                    if widget['name'] in ['Integrate Q Lower?',
                            'Integrate Q Upper?','Integrate Number Of Q?']:
                        self.GUI.changeQor2Theta('Work in Q')
                    if widget['name'] in ['Integrate 2theta Lower?',
                            'Integrate 2theta Upper?',
                            'Integrate Number Of 2theta?']:
                        self.GUI.changeQor2Theta('Work in 2theta')

                    if widget['name'] in ['Cake Q Lower?','Cake Q Upper?',
                            'Cake Number Of Q?']:
                        self.GUI.changeQor2Theta('Work in Q')
                    if widget['name'] in ['Cake 2theta Lower?',
                            'Cake 2theta Upper?','Cake Number Of 2theta?']:
                        self.GUI.changeQor2Theta('Work in 2theta')


                    value = macro.next()
                    if VERBOSE: print ' - current: ',value 
                    # Put the number in the entry field
                    if widget in self.allEntryFieldsRequiringFloat:
                        widget['widget'].setentry(float(value))
                    if widget in self.allEntryFieldsRequiringInt:
                        widget['widget'].setentry(int(value))

            for widget in self.allScales:
                if cleanline == widget['clean name']:
                    if moveAround: widget['move to page']()
                    if ALLOWABORT: self.abortDisplay.main.show()
                    if ALLOWABORT: self.abortDisplay.button.update()
                    value = macro.next()
                    if VERBOSE: print ' - current: ',value 
                    # Set the scale
                    widget['widget'].set(float(value))

            for widget in self.allColorMaps:
                if cleanline == widget['clean name']:
                    if moveAround: widget['move to page']()
                    if ALLOWABORT: self.abortDisplay.main.show()
                    if ALLOWABORT: self.abortDisplay.button.update()
                    colormap = macro.next()
                    if VERBOSE: print ' - current: ',colormap

                    # do the stripping because we don't want color 
                    # maps that look like "   copper"
                    # to be rejected.
                    widget['widget'].setvalue(colormap.strip())

            for widget in self.allColorInputs:
                if cleanline == widget['clean name']:
                    if moveAround: widget['move to page']()
                    if ALLOWABORT: self.abortDisplay.main.show()
                    if ALLOWABORT: self.abortDisplay.button.update()
                    color = macro.next().lower() 
                    if VERBOSE: print ' - current: ',color
                    # set the color
                    widget['function'](color) 

            for widget in self.allSaveMenuItemsRequiringFilename: 
                if cleanline == widget['clean name']:

                    filename = macro.next()
                    # create the folder the file is in (if it 
                    # doesn't exit).
                    General.createFolderForFile(filename.strip())

                    if VERBOSE: print ' - current: ',filename
                    # Set the filename
                    widget['function'](filename.strip())
            
            for widget in self.allCheckBoxMenuItems:
                if cleanline == widget['clean name']:
                    widget['function']()

            # there is only one standard Q thing so technically, 
            # we could just do a straight compare,
            # but I want to keep the notation the same
            for widget in self.standardQMenuItem:
                if cleanline == widget['clean name']:
                    if moveAround: widget['move to page']()
                    if ALLOWABORT: self.abortDisplay.main.show()
                    if ALLOWABORT: self.abortDisplay.button.update()
                    standard = macro.next()
                    if VERBOSE: print ' - current: ',standard
                    widget['function'](standard.strip())

            # look at the next line in the macro file

            line = macro.next()

            # refresh the GUI so it looks like the GUI is doing things
            # Otherwise the GUI gets unresponsive while the macro is running.
            # This function could cause trouble, especially if the macro
            # is called as part of a call back. If any trouble arises, this
            # line can simply be commented out. More information on this at
            # http://www.pythonware.com/library/tkinter/introduction/x9374-event-processing.htm
            if ALLOWABORT: self.abortDisplay.main.show()
            if ALLOWABORT: self.abortDisplay.button.update()
            self.GUI.xrdwin.update()

        self.CANCEL_FLAG  = None
        self.abortDisplay.main.withdraw()
        
        # remove the macro notice from the screen
        self.GUI.macrostatus.pack_forget() 
        self.setstatus(self.GUI.macrostatus,'')
 
    def macroRecord(self,event,typeOfEvent):
        """
            Record a single GUI command as a macro line.

            This function does not deal with the macro 
            lines since I can't figure out how to 
            bind to pushing of the menu bar:
                * Work in eV
                * Work in Lambda
                * Work in 2theta
                * Work in Q
                * Standard Q
                * Save Diffraction Image

            Furthermore, I need to do explicit macro 
            calling for all of the inputs dealing with filenames.
            So this function does not deal with them.

                * Data File:
                * Q Data:
                * Load From File:
                * Save To File
                * Save Last Fit
                * Make/Save Peak List
                * Save Mask
                * Load Mask
                * Save Caked Image
                * Save Caked Data
                * Save Integration Data
        """
        widget = event.widget

        for checkbutton in self.allCheckBoxes:
            if widget == checkbutton['widget']:

                if checkbutton['name'] == 'lambda Fixed:' and \
                        self.GUI.eVorLambda.get() == 'Work in eV':
                    continue
                if checkbutton['name'] == 'E Fixed:' and \
                        self.GUI.eVorLambda.get() == 'Work in Lambda':
                    continue

                if len(self.GUI.macroLines)>=2 and \
                        self.GUI.macroLines[-2]==checkbutton['name']:
                    self.GUI.macroLines.pop()
                    self.GUI.macroLines.pop()
                self.GUI.macroLines.append(checkbutton['name'])
                if checkbutton['var'].get():
                    self.GUI.macroLines.append('\tSelect')
                else:
                    self.GUI.macroLines.append('\tDeselect')
                return # no reason to look further

        # Do all the entry fields at once
        for entryField in self.allLoadEntryFieldsRequiringFilename + \
                self.allEntryFieldsRequiringFloat + \
                self.allEntryFieldsRequiringInt:

            if widget == entryField['widget'].component('entry'):
                if len(self.GUI.macroLines)>1 and \
                        self.GUI.macroLines[-2]==entryField['name']:
                    self.GUI.macroLines.pop()
                    self.GUI.macroLines.pop()

                if typeOfEvent=='key': 
                    #only do macro record if the user types something

                    if entryField['name'] == 'lambda:' and \
                            self.GUI.eVorLambda.get() == 'Work in eV':
                        continue
                    if entryField['name'] == 'E:' and \
                            self.GUI.eVorLambda.get() == 'Work in Lambda':
                        continue

                    # Dont' record if the GUI is in the other state

                    if entryField['name'] in ['Integrate Q Lower?', \
                            'Integrate Q Upper?','Integrate Number Of Q?'] and \
                            self.GUI.Qor2Theta.get() == 'Work in 2theta':
                        continue

                    if entryField['name'] in ['Integrate 2theta Lower?', \
                            'Integrate 2theta Upper?','Integrate Number Of 2theta?']\
                            and self.GUI.Qor2Theta.get() == 'Work in Q':
                        continue

                    if entryField['name'] in ['Cake Q Lower?', \
                            'Cake Q Upper?','Cake Number Of Q?'] and \
                            self.GUI.Qor2Theta.get() == 'Work in 2theta':
                        continue

                    if entryField['name'] in ['Cake 2theta Lower?', \
                            'Cake 2theta Upper?','Cake Number Of 2theta?']\
                            and self.GUI.Qor2Theta.get() == 'Work in Q':
                        continue

                    val = entryField['widget'].getvalue()
                    self.GUI.macroLines.append(entryField['name'])
                    self.GUI.macroLines.append('\t'+val)
                return # no reason to look further


        for colorMap in self.allColorMaps:
            # you need to compare to the part of the Pmw object 
            # that is actually pushed since a Pmw object is really 
            # made up out of several smaler Tkinter things.
            if widget == colorMap['widget'].component('listbox'):

                if len(self.GUI.macroLines)>1 and \
                        self.GUI.macroLines[-2]==colorMap['name']:
                    self.GUI.macroLines.pop()
                    self.GUI.macroLines.pop()

                self.GUI.macroLines.append(colorMap['name'])
                self.GUI.macroLines.append('\t'+colorMap['widget'].getvalue()[0])
                return # no reason to look further

        for color in self.allColorInputs:
            if widget == color['widget']:
                if len(self.GUI.macroLines)>1 and \
                        self.GUI.macroLines[-2]==color['name']:
                    self.GUI.macroLines.pop()
                    self.GUI.macroLines.pop()

                self.GUI.macroLines.append(color['name'])
                self.GUI.macroLines.append('\t'+color['var'].get())

        for scale in self.allScales:
            if widget == scale['widget']:
                if len(self.GUI.macroLines)>1 and \
                        self.GUI.macroLines[-2]==scale['name']:
                    self.GUI.macroLines.pop()
                    self.GUI.macroLines.pop()

                self.GUI.macroLines.append(scale['name'])
                self.GUI.macroLines.append('\t'+str(scale['widget'].get()))

        for button in self.allOtherButtons:
            if widget == button['widget']:

                if button['name'] in ['AutoIntegrate Q-I','Integrate Q-I'] and \
                        self.GUI.Qor2Theta.get() == 'Work in 2theta':
                    continue
                if button['name'] in ['AutoIntegrate 2theta-I',
                        'Integrate 2theta-I'] and \
                        self.GUI.Qor2Theta.get() == 'Work in Q':
                    continue

                if len(self.GUI.macroLines)>0 and \
                        self.GUI.macroLines[-1]==button['name']:
                    self.GUI.macroLines.pop()

                self.GUI.macroLines.append(button['name'])

        # these two can't be done by this function, 
        # so they will be called explicitly
        #   self.allLoadButtonsRequiringFilename 
        #   self.allSaveButtonsRequiringFilename 
        #   self.allSaveMenuItemsRequiringFilename 
        

    def explicitMacroRecordTwoLines(self,first,second):
        """ This one is needed for the standard Q data. """
        if len(self.GUI.macroLines)>1 and self.GUI.macroLines[-2]==first:
            self.GUI.macroLines.pop()
            self.GUI.macroLines.pop()
        self.GUI.macroLines.append(first)
        self.GUI.macroLines.append(second)


    def explicitMacroRecordOneLine(self,line):
        """ There are a couple of macro commands I can 
            get the binding to catch. The commands are:
                * Work in eV
                * Work in Lambda
                * Work in 2theta
                * Work in Q
            So I have my program explicitly call this 
            function to set the macro
        """
        if len(self.GUI.macroLines)>0 and self.GUI.macroLines[-1]==line:
            self.GUI.macroLines.pop()
        self.GUI.macroLines.append(line)


    def testMacroValidity(self,filename):
        # test the file
        file = open(filename,'r')

        currentline = file.readline().strip()
        linenumber = 1
        cleanline = cleanstring(currentline.lower())

        while currentline:
            if cleanline[0] == '#' or cleanline == '':
                # comment lines are all right and so are blank lines
                pass
            elif valueInListOfDict(self.allEntryFieldsRequiringFloat,
                    'clean name',cleanline):
                nextline = file.readline().strip()
                if not nextline:
                    file.close()
                    raise UserInputException("""%s is not a valid \
macro file because line %d ("%s") must be followed by a \
number""" % (filename,linenumber,currentline) )
                try:
                    float(nextline)
                except:
                    file.close()
                    raise UserInputException("""%s is not a valid \
macro file because line %d ("%s") must be followed by a valid \
number""" % (filename,linenumber,currentline) )
                linenumber += 1

            elif valueInListOfDict(self.allEntryFieldsRequiringInt,
                    'clean name',cleanline):
                nextline = file.readline().strip()
                if not nextline:
                    file.close()
                    raise UserInputException("""%s is not a valid \
macro file because line %d ("%s") must be followed by an 
integer""" % (filename,linenumber,currentline) )
                try:
                    int(nextline)
                except:
                    file.close()
                    raise UserInputException("""%s is not a valid \
macro file because line %d ("%s") must be followed by a valid \
integer""" % (filename,linenumber,currentline) )
                linenumber += 1
            elif valueInListOfDict(self.allScales,'clean name',cleanline):
                nextline = file.readline().strip()
                if not nextline:
                    file.close()
                    raise UserInputException("""%s is not a valid \
macro file because line %d ("%s") must be followed by a number \
between 0 and 1""" % (filename,linenumber,currentline) )
                try:
                    float(nextline)
                except:
                    file.close()
                    raise UserInputException("""%s is not a valid \
macro file because line %d ("%s") must be followed by a valid number \
between 0 and 1""" % (filename,linenumber,currentline) )
                if float(nextline)<0 or float(nextline)>1:
                    file.close()
                    raise UserInputException("""%s is not a valid \
macro file because line %d ("%s") must be followed by a valid \
number between 0 and 1""" % (filename,linenumber,currentline) )
                linenumber += 1

            elif valueInListOfDict(self.allCheckBoxes,'clean name',cleanline):
                nextline = cleanstring(file.readline().lower())
                if not nextline or not nextline in ['select','deselect']:
                    file.close()
                    raise UserInputException("""%s is not a valid \
macro file because line %d ("%s") must be followed by the line \
"Select" or "Deselect".""" % (filename,linenumber,currentline) )
                linenumber += 1

            elif valueInListOfDict(self.allCheckBoxMenuItems,'clean name',cleanline):
                # nothing follows
                pass

            elif valueInListOfDict(self.allColorMaps,'clean name',cleanline):
                nextline = cleanstring(file.readline())
                if not nextline or not \
                        nextline in self.GUI.colorMaps.getColorMapNames():
                    file.close()
                    raise UserInputException("""%s is not a valid \
macro file because line %d ("%s") must be followed by a line with \
a valid color map.""" % (filename,linenumber,currentline) )
                linenumber += 1

            elif valueInListOfDict(self.standardQMenuItem,'clean name',cleanline):
                nextline = file.readline().strip()
                if not nextline: 
                    file.close()
                    raise UserInputException("""%s is not a valid \
macro file because line %d ("%s") must be followed by a standard Q \
file name""" % (filename,linenumber,currentline) )
                linenumber += 1

            elif valueInListOfDict(self.dataFileCommand,'clean name',cleanline):
                # Test if it is a valid "Data File:" line
                # This can be any number of file or folder names all separated
                # by some sort of whitespace.
                nextline = file.readline().strip()
                if not nextline: 
                    file.close()
                    raise UserInputException("""%s is not a valid \
macro file because line %d ("%s") must be followed by filenames \
and foldernames""" % (filename,linenumber,currentline) )

                # this will raise an error if the line is not valid
                # the error will be pretty for the user.
                expandDataFile(nextline,filename,linenumber,currentline)
                linenumber += 1

            elif valueInListOfDict(self.multipleDataFilesCommand,
                    'clean name',cleanline):
                # Test if it is a valid "Multiple Data Files:".
                # This can be a list of folder names and of lists enclosed by [ ] 
                # Inside of the [ ] can be a list of file names all separated
                # by some sort of white space

                nextline = file.readline().strip()
                if not nextline: 
                    file.close()
                    raise UserInputException("""%s is not a valid \
macro file because line %d ("%s") must be followed by a filenames \
and foldernames""" % (filename,linenumber,currentline) )

                # this will raise an error if the line is not valid
                # the error will be pretty for the user.
                expandMultipleDataFiles(nextline,filename,linenumber,currentline)
                linenumber += 1

            elif valueInListOfDict(self.allLoadEntryFieldsRequiringFilename+ \
                    self.allLoadButtonsRequiringFilename,'clean name',cleanline):
                nextline = file.readline().strip()
                if not nextline: 
                    file.close()
                    raise UserInputException("""%s is not a valid \
macro file because line %d ("%s") must be followed by a \
filename""" % (filename,linenumber,currentline) )
                # if the filename does not contain "PATHNAME", "FILENAME",
                # "FOLDERPATH", and "FOLDERNAME", and
                # if it dose not exist, then we must raise an error
                if nextline.find('PATHNAME') == -1 and \
                        nextline.find('FILENAME') == -1 and \
                        nextline.find('FOLDERPATH') == -1 and \
                        nextline.find('FOLDERNAME') == -1 and \
                        not os.path.isfile(nextline):
                    file.close()
                    raise UserInputException("""%s is not a valid \
macro file because line %d ("%s") is followed by the filename "%s" \
which does not exist""" % (filename,linenumber,currentline,nextline) )
                linenumber += 1

            elif valueInListOfDict(self.allOtherButtons,'clean name',cleanline):
                # Nothing to check with the other buttons
                pass

            elif valueInListOfDict(self.allSaveMenuItemsRequiringFilename+ \
                    self.allSaveButtonsRequiringFilename,'clean name',cleanline):
                nextline = file.readline().strip()
                if not nextline:
                    file.close()
                    raise UserInputException("""%s is not a valid \
macro file because line %d ("%s") must be followed by a line with \
a Q data file.""" % (filename,linenumber,currentline) )
                linenumber += 1

            elif valueInListOfDict(self.allColorInputs,'clean name',cleanline):
                nextline = cleanstring(file.readline())
                if not nextline:
                    file.close()
                    raise UserInputException("""%s is not a valid \
macro file because line %d ("%s") must be followed by a line with \
a valid color.""" % (filename,linenumber,currentline) )
                linenumber += 1

            else:
                raise UserInputException("""%s is not a valid macro \
file because line %d ("%s") is not a recognized macro \
line.""" % (filename,linenumber,currentline) )

            currentline = file.readline().strip()
            linenumber += 1
            cleanline = cleanstring(currentline.lower())

        file.close()


    def startRecordMacro(self):
        # keep all the macro lines to save to a file 
        self.GUI.macroLines = []

        self.GUI.macrostatus.pack(side=RIGHT)
        self.setstatus(self.GUI.macrostatus,'Recording Macro')

        self.GUI.xrdwin.bind_all(sequence='<ButtonRelease>',
                func=lambda event,self=self:self.macroRecord(event,'button') )
        self.GUI.xrdwin.bind_all(sequence='<KeyRelease>',
                func=lambda event,self=self:self.macroRecord(event,'key') )

        # Change the enabled/disabled status of a menu item so you can't try to
        # run a macro while recording a macro. Code inspired by:
        # http://mail.python.org/pipermail/tkinter-discuss/2004-September/000204.html
        self.GUI.macromenu.entryconfig(
            self.GUI.macromenu.index('Start Record Macro'),state=DISABLED)
        self.GUI.macromenu.entryconfig(
            self.GUI.macromenu.index('Stop Record Macro'),state=NORMAL)
        self.GUI.macromenu.entryconfig(
            self.GUI.macromenu.index('Set As Initialization'),state=NORMAL)
        self.GUI.macromenu.entryconfig(
            self.GUI.macromenu.index('Run Saved Macro'),state=DISABLED)
        self.GUI.macromenu.entryconfig(
            self.GUI.macromenu.index('Clear Initialization'),state=DISABLED)


    def makeClearInitializationOptionRight(self):

        if os.path.isfile('Preferences/InitializationMacro.dat'):
            self.GUI.macromenu.entryconfig(
                self.GUI.macromenu.index('Clear Initialization'),state=NORMAL)
        else:
            self.GUI.macromenu.entryconfig(
                self.GUI.macromenu.index('Clear Initialization'),state=DISABLED)
         

    def clearInitialization(self):

        if os.path.isfile('Preferences/InitializationMacro.dat'):
            os.remove('Preferences/InitializationMacro.dat')

        self.makeClearInitializationOptionRight()
            

    def setAsInitialization(self):

        self.GUI.macrostatus.pack_forget() # remove from screen
        self.setstatus(self.GUI.macrostatus,'')

        self.GUI.xrdwin.unbind_all(sequence='<ButtonRelease>')
        self.GUI.xrdwin.unbind_all(sequence='<KeyRelease>')

        if not os.path.isdir('Preferences'):
            os.mkdir('Preferences')

        if self.GUI.macroLines == None or len(self.GUI.macroLines) < 1:
            # no macro commands, so delete the file with macro lines in it

            if os.path.isfile('Preferences/InitializationMacro.dat'):
                os.remove('Preferences/InitializationMacro.dat')
            return
            
        # save this to a file to preserve state
        file = open('Preferences/InitializationMacro.dat','w')
        file.write("# Initialization Macro File recorded on "+time.asctime()+"\n")
        for line in self.GUI.macroLines:
            file.write(line+"\n")
        file.close()

        # no more being in a macro
        self.GUI.macroLines = None
        
        self.GUI.macromenu.entryconfig(
            self.GUI.macromenu.index('Start Record Macro'),state=NORMAL)
        self.GUI.macromenu.entryconfig(
            self.GUI.macromenu.index('Stop Record Macro'),state=DISABLED)
        self.GUI.macromenu.entryconfig(
            self.GUI.macromenu.index('Set As Initialization'),state=DISABLED)
        self.GUI.macromenu.entryconfig(
            self.GUI.macromenu.index('Run Saved Macro'),state=NORMAL)
        self.makeClearInitializationOptionRight()


    def stopRecordMacro(self):

        self.GUI.macrostatus.pack_forget() # remove from screen
        self.setstatus(self.GUI.macrostatus,'')

        self.GUI.xrdwin.unbind_all(sequence='<ButtonRelease>')
        self.GUI.xrdwin.unbind_all(sequence='<KeyRelease>')

        self.GUI.macromenu.entryconfig(
            self.GUI.macromenu.index('Start Record Macro'),state=NORMAL)
        self.GUI.macromenu.entryconfig(
            self.GUI.macromenu.index('Stop Record Macro'),state=DISABLED)
        self.GUI.macromenu.entryconfig(
            self.GUI.macromenu.index('Set As Initialization'),state=DISABLED)
        self.GUI.macromenu.entryconfig(
            self.GUI.macromenu.index('Run Saved Macro'),state=NORMAL)
        self.makeClearInitializationOptionRight()

        if self.GUI.macroLines == None or len(self.GUI.macroLines) < 1:
            # no macro commands, nothing to do
            self.GUI.macroLines = None
            return
            
        defaultextension = ".dat"
        filename = tkFileDialog.asksaveasfilename(
                filetypes=[ ('dat file','*.dat'), ("All files", "*"), ], 
                defaultextension = defaultextension,
                initialdir=self.GUI.defaultDir,
                title="Save Macro")

        if filename in ['',()]: 
            for line in self.GUI.macroLines:
                print '  '+line
            print
        else:
            # on the mac, it won't give a default extension if you don't write
            # it out explicitly, so make sure to do so automatically otherwise.
            if os.path.splitext(filename)[1] == '':
                filename += defaultextension

            file = open(filename,'w')

            file.write("# Macro File recorded on "+time.asctime()+"\n")
            for line in self.GUI.macroLines:
                file.write(line+"\n")

        # no more being in a macro
        self.GUI.macroLines = None


class Macro:
    r""" Macro proves an object for easy reading of a macro 
        file. The purpose of this object is to create an object which 
        will return a line from the macro file each time a call to 
        next() is issued. But this object gets rid of any of the fancy
        mark up in the macro file so that each line returned can
        directly be run as a command on the Gui.
        
        First of all, the object removes beginning and ending 
        white spaces, tabs, and newlines from the lines.

        It will act as though there are no empty or comment lines in
        the file.

        Then, the program will take any of the lines of the from 
        'data file' and will then look and what files the user is 
        asking to load. For each of those files, it will look at all
        the commands that the user is using for each of them and make
        it look like the user calls 'data file' separately on each of 
        the lines. So in effect, this object removes any of them 
        looping allowed in a macro file by simply giving redundant 
        commands as though there was no looping at all.
        
        This code will also look into any directories of data that 
        are given and pull out each of the files to run, so that 
        when lines are taken from the object, the user will only 
        think they have to deal with specific files.

        Finally, this object will look for any occasion when the
        macro is in a loop and will replace the word FILENAME with
        the file name of the current diffraction file. It will also
        replace the work PATHNAME with the path leading to the FILENAME.
        So inside a loop, PATHNAME/FILENAME.mar3450 is the name of the current
        file that is being operated on. That can let the user, for
        example, save the cake data with a corresponding name for
        each of the files that they are looping over.

        It will also replace FOLDERNAME with the name of the folder
        that the current diffraction file is in and it will replace
        FOLDERPATH with the path leading up to the folder contaning
        the folder with the file in it.

        Here are some doctests to explain how the object works

        To begin, we first create a temp file with some macro commands in it.

            >>> import tempfile
            >>> tempFile = tempfile.mktemp()
            >>> file = open(tempFile,'w')
            >>> file.write('# Comment line\n')
            >>> file.write('\n')
            >>> file.write('Draw Q Lines?\n')
            >>> file.write('    Select\n')
            >>> file.write('Draw dQ Lines?\n')
            >>> file.write('    Deselect\n')
            >>> file.write('Data File:\n')
            >>> file.write('c:\\firstfile.mar3450\tc:\\secondfile.mar3450\n') 
            >>> file.write('Do Cake\n')
            >>> file.write('Data File:\n')
            >>> file.write('c:\\thirdfile.mar3450 c:\\fourthfile.mar3450\n')
            >>> file.write('Draw Q Lines?\n')
            >>> file.write('    Select\n')
            >>> file.write('Draw dQ Lines?\n')
            >>> file.write('    Deselect\n')
            >>> file.write('END LOOP\n')
            >>> file.write('Data File:\n')
            >>> file.write('c:\\fifthfile.mar3450')
            >>> file.close()

        Then, we create a Macro object see what it returns

            >>> macro = Macro(tempFile)
            >>> print macro.next()
            Draw Q Lines?
            >>> print macro.next()
                Select
            >>> print macro.next()
            Draw dQ Lines?
            >>> print macro.next()
                Deselect

        Here, we go through the first loop in execution
        
            >>> print macro.next()
            Data File:
            >>> print [macro.next()]
            ['\tc:\\firstfile.mar3450']
            >>> print macro.next()
            Do Cake

            >>> print macro.next()
            Data File:
            >>> print [macro.next()]
            ['\tc:\\secondfile.mar3450']
            >>> print macro.next()
            Do Cake

        The last file to read in has no commands associated with it

            >>> print macro.next()
            Data File:
            >>> print [macro.next()]
            ['\tc:\\thirdfile.mar3450']
            >>> print macro.next()
            Draw Q Lines?
            >>> print macro.next()
                Select
            >>> print macro.next()
            Draw dQ Lines?
            >>> print macro.next()
                Deselect

            >>> print macro.next()
            Data File:
            >>> print [macro.next()]
            ['\tc:\\fourthfile.mar3450']
            >>> print macro.next()
            Draw Q Lines?
            >>> print macro.next()
                Select
            >>> print macro.next()
            Draw dQ Lines?
            >>> print macro.next()
                Deselect

            >>> print macro.next()
            Data File:
            >>> print [macro.next()]
            ['\tc:\\fifthfile.mar3450']

        When there are no more lines, the object only returns None
            >>> print macro.next()
            None
            >>> print macro.next()
            None

    """
    def __init__(self,filename):

        file = open(filename,'rU')
        temp = file.readlines()
        self.lines = []

        file.close()

        for line in temp:
            cleanline = cleanstring(line)

            if cleanline != '' and cleanline[0] != '#':
                self.lines.append({'line':line.rstrip(),'clean line':cleanline})

        self.currentline = 0
        self.loopBeginLine = None
        self.currentDiffractionFile = None
        self.allDiffractionFiles = []
        self.nextMustBe = None
        self.inLoop = None

    def next(self):
        # if we have gotten to the end of the file and are not in a loop, exit
        if self.currentline >= len(self.lines) and not self.inLoop:
            return None

        if self.currentline >= len(self.lines) and self.inLoop:
            # At end of macro file while in a loop

            # if at end of loop, exit macro
            if self.allDiffractionFiles == []:
                self.currentDiffractionFile = None
                self.inLoop = 0
                self.nextMustBe = None
                return None

            # otherwise, go to the beginning of the loop with a new file from the list
            self.currentDiffractionFile = self.allDiffractionFiles.pop()
            self.nextMustBe = self.currentDiffractionFile
            # This is a bit tricky, but the next thing to give is the 
            # line "Data File:"
            # But after this, our code must go onto a line with just 
            # the filename of the
            # next file to analize. To do this, we make sure our 
            # code goes into a new execution
            self.currentline = self.loopBeginLine-1
            return self.lines[self.currentline-1]['line']

        if self.nextMustBe != None:
            temp = self.nextMustBe
            self.nextMustBe = None
            self.currentline+=1
            return temp

        # if the last line was a data file or multiple data file line
        if self.lines[self.currentline-1]['clean line'] in ["data file",
                "multiple data files"]:
            # if we got here without coming back to it, find all files 
            # in it and start loop
            if not self.inLoop:
                if self.lines[self.currentline-1]['clean line']=="data file":
                    self.allDiffractionFiles = expandDataFile(
                            self.lines[self.currentline]['line'])
                else:
                    self.allDiffractionFiles = expandMultipleDataFiles(
                            self.lines[self.currentline]['line'])

                self.currentDiffractionFile = self.allDiffractionFiles.pop(0)
                self.currentline+=1
                self.inLoop = 1
                self.loopBeginLine = self.currentline
                return self.currentDiffractionFile

        line = self.lines[self.currentline]['line']
        cleanline = self.lines[self.currentline]['clean line']

        # the end of the loop in the text can happen if the current line is
        # "END LOOP", "data file:", "multiple data file",  or if we have 
        # stepped outside the image
        if self.inLoop and cleanline in ['end loop','data file', \
                'multiple data files']:
            # once we get to the end of the loop, we must make a decision.
            # if we have looked through all the files in the loop
            # we want to exit
            if self.allDiffractionFiles == []:
                self.currentDiffractionFile = None
                self.inLoop = 0
                self.nextMustBe = None

                if cleanline in ['data file','multiple data files']:
                    # if the current line is data file or multiple data 
                    # files, we want to continue 
                    # execution on this line as though we just came to it.
                    # So, no advance
                    return self.next()
                else:
                    # advance to the next line in the file
                    self.currentline += 1
                    return self.next()
                
            
            # otherwise, go to the beginning of the loop with a new file from the list
            self.currentDiffractionFile = self.allDiffractionFiles.pop()
            self.nextMustBe = self.currentDiffractionFile
            # This is a bit tricky, but the next thing to give is the line 
            # "Data File:" or "Multiple Data Files:"
            # But after this, our code must go onto a line with just the 
            # filename of the next file to analize. To do this, we make 
            # sure our code goes into a new execution
            self.currentline = self.loopBeginLine-1
            return self.lines[self.currentline-1]['line']

        # try to parse the line to replace PATHNAME with the 
        # path of the current
        # diffraction file and FILENAME with the corresponding 
        # file.
        # This would mean that our current diffraction file 
        # is PATHNAME/FILENAME.mar3450
        # Replace FOLDERPATH with the path leading up to the
        # folder and FOLDERNAME with the name of the folder.
        if self.currentDiffractionFile != None:
            pathname,filename = self.getPathAndFilename(self.currentDiffractionFile)
            pathname = removeTrailingCharacters(pathname,[os.sep])
            line = line.replace('PATHNAME',pathname)

            basename = os.path.splitext(filename)[0]
            line = line.replace('FILENAME',basename)

            # splitting the path gets out the folder 
            folderpath,foldername = os.path.split(pathname)
            line = line.replace('FOLDERPATH',folderpath)
            line = line.replace('FOLDERNAME',foldername)

        self.currentline += 1
        return line


    def getPathAndFilename(self,string):
        string = string.strip()
        # test if it is of the form "[ file_one file_two ]" or if 
        # it is of the form "file_one"
            
        # this regexp will pull out anyting inside of the [ ... ]

        bracketpattern= r"""\[(.*?)\]"""
        bracketregexp = re.compile(bracketpattern, re.DOTALL)
        brackets = bracketregexp.findall(string)
        if len(brackets) == 0:
            # then it is of the form "file_one"
            # with NO brackets, then just look
            # at the one file
            path,filename = os.path.split(string)
        else:
            # otherwise, it is a list of files inside 
            # the string, so break them up
            files = General.splitPaths(brackets[0])

            # since they all have the same path, just look at the first one
            path = os.path.split(files[0])[0]
            filename = "MULTIPLE_FILES"
        
        return path,filename


def testProperBrackets(string):
    """ This function takes in a string and determines
        if the number and order of brackets is allowed for
        a macro line which follows a "Multiple Data Files" line.
        This string can contain lists bracketed off like [ ... ]
        and it can contain any number of these. But every opening
        bracket must be closed, there can be no nested brackets,
        and a closing bracket must always close an opening 
        bracket."""
        
    leftfound = 0 # if we have found a left bracket yet

    # go through the string
    for index in range(len(string)): 

        # if we find a left bracket
        if string[index] == '[': 

            # error if we've already found a left bracket
            if leftfound == 1: 
                return 0
            
            # otherwise say that we've already found this one
            leftfound = 1

        # if we find a right bracket
        if string[index] == ']':
            
            # error if we haven't yet found an opening bracket
            if leftfound == 0:
                return 0

            # otherwise, this closing bracket closes the last open bracket.
            leftfound = 0
    
    # error if we are left with an open bracket
    if leftfound != 0:
        return 0

    # otherwise, the string looks good
    return 1
        

def expandMultipleDataFiles(string,filename='',linenumber=-1,currentline=0):
    """ Takes in a string which is a list of file and folder 
        names. This string can contain list of file names 
        enclosed in [ and ] brackets. These lists msut be of 
        the form 

            "[ file1 file2 file3 ... ]"
        
        All of the filenames within brackets much be from the 
        same folder, they must all be of the same extension, 
        and they must all exist. There can be as many of these 
        lists as desired
        put next to eachother in the string. In addition, there
        can be folders in this list. Any of the folders must
        be real folders and there can be no stand alone folders.
        So in total, the input will look something like
            
            "[ file1 file2 file3 ] folder1 [ file4 file 6] folder 2
        
        The output of this function is a list of strings each
        of the form

            "[ file1 file2 file3 ... ]"

        The lists are taken from the input string and by looking
        inside each of the folders. The program will take all of
        the diffraction files from each of the subfolders and
        the given folders and put them into their own lists. 
        So it just makes a bunch of [ and ] bracket enclosed lists 
        and returns them.

        An exception is rasied if any of the files or folders 
        do not exist. An exception is raised if folders are given
        inside of brackets or files outside of them. An exception
        is raised if any of the files inside of a particular bracket
        have different paths, different extensions, or are of different
        file formats. An exception is also raised if the program can't
        find any files to put into bracketed lists to return to the
        user (IE, if only a folder is given and nothing is in the folder).

        filename, linenumber, and currentline are used to format nice 
        exceptions but are optional. """

    # get all the lists of file names bracketed off with[]
    pattern = r"""\[.*?\]"""
    regexp = re.compile(pattern, re.DOTALL)
    brackets = regexp.findall(string)

    allDiffractionFiles = []

    if not testProperBrackets(string):
        raise UserInputException("""%s is not a valid macro file \
because line %d ("%s") is followed by the line ("%s") which does \
not contain properly nested brackets \
[ and ].""" % (filename,linenumber,currentline,string) )

    # check if each of the files in the bracket is a real file
    for loop in brackets:
        
        # get rid of the brackets
        bracket = loop[1:-1]
        try:
            # get all files within brackets
            split = General.splitPaths(bracket)
        except:
            raise UserInputException("""%s is not a valid macro \
file because line %d ("%s") is followed by the line ("%s") which \
contains the expression %s which cannot be parsed into unique \
existing filenames.""" % (filename,linenumber,currentline,string,loop) )

        # do no analysis on this bracketed list if there are
        # no items in it
        if len(split) < 1:
            continue

        for each in split:
            # ensure all the files in each bracket exist
            if not os.path.isfile(each):
                raise UserInputException("""%s is not a valid macro \
file because line %d ("%s") is followed by the line ("%s") which \
contains the term %s which contains some things that are not \
all files. Only files can come between [ and ] \
brackets.""" % (filename,linenumber,currentline,string,loop) )

            # ensure all the files in each bracket have the same 
            # directory
            if os.path.dirname(each) != os.path.dirname(split[0]):
                raise UserInputException("""%s is not a valid macro \
file because line %d ("%s") is followed by the line ("%s") which \
contains the term %s which contains several files from diffrent \
directories. All files loaded into the program with the [ and ] \
notation must be from the same folder. This is to ensure that the \
PATHNAME, FILENAME, FOLDERNAME, and FOLDERPATH syntax remain \
meaningful""" % (filename,linenumber,currentline,string,loop) )
            
            # ensure all the files in each bracket have the same
            # extension
            if General.getextension(each) != General.getextension(split[0]):
                raise UserInputException("""%s is not a valid macro \
file because line %d ("%s") is followed by the line ("%s") which \
contains the term %s which contains several files with different \
extensions. All diffraction files within a [ and ] bracket must \
have the same extension. """ % (filename,linenumber,currentline,string,loop) )

        # If no errors were raised and all the files in the bracket
        # are good, all the bracket to the return list
        allDiffractionFiles.append('\t'+loop)

    # get all the folders inbetween ] ... [
    pattern = r"""\]([^\[\]]*?)\["""
    regexp= re.compile(pattern, re.DOTALL)
    folderstrings = regexp.findall(string)

    # get all folders before the first [
    pattern = r"""^([^\[\]]*?)\["""
    regexp= re.compile(pattern, re.DOTALL)
    folderstrings += regexp.findall(string)

    # get all folders after the last ]
    pattern = r"""\]([^\[\]]*?)$"""
    regexp= re.compile(pattern, re.DOTALL)
    folderstrings += regexp.findall(string)

    # get all folders when there are no [
    # or ] in the entire string
    pattern = r"""^([^\[\]]*?)$"""
    regexp= re.compile(pattern, re.DOTALL)
    folderstrings += regexp.findall(string)

    folders = []
    # loop over all the strings containing folders
    for temp in folderstrings:
        try:
            # get all the acutal folders names from the string
            split = General.splitPaths(temp)
            folders += split
        except UserInputException:
            raise UserInputException("""%s is not a valid macro \
file because line %d ("%s") is followed by the line ("%s") and \
because it contains the expression %s which cannot be parsed into \
unique existing folders.""" % (filename,linenumber,currentline,string,temp) )

    # now, all the user input folders are in the folders array

    for folder in folders:
        # make sure all the folders are direcotires
        if not os.path.isdir(folder.strip()):
            raise UserInputException("""%s is not a valid macro file \
because line %d ("%s") is followed by the line ("%s") and because it \
contains the expression %s which is not an existing \
folder.""" % (filename,linenumber,currentline,string,folder) )
    
    # loop over all given folders
    for folder in folders:
        # find all subfolders
        subfolders = General.getallsubfolders(folder)
        
        # loop over the subfolders
        for subfolder in subfolders:
            # get all files in the subfolder
            files = General.getallfileswithextensions(subfolder,allExtensions)
            allFilesInSubfolder = []

            # loop over all the files in the subfolder
            for file in files:
                extension = General.getextension(file)

                # make sure all the files that are found have
                # the same extension
                if extension != General.getextension(files[0]):
                    raise UserInputException("""%s is not a valid \
macro file because line %d ("%s") is followed by the line ("%s") \
and because it contains the folder %s which has the subfolder \
%s which contains diffraction data of several different file \
formats. A macro can only add togethers files from subfolders \
if they are all of the same file \
format.""" % (filename,linenumber,currentline,string,folder,subfolder) )

                # add all the diffraction files to a list
                allFilesInSubfolder.append(
                        " "+os.path.join(folder,subfolder,file))

            # if there are some files in the subfolder, add
            # them to the return list bracketed off
            if len(allFilesInSubfolder) > 0:
                allDiffractionFiles.append('\t[ '+ \
                        General.joinPaths(allFilesInSubfolder)+' ]')

    # Raise an error if no return stuff was found
    if len(allDiffractionFiles) < 1:
        raise UserInputException("""%s is not a valid macro file \
because line %d ("%s") is followed by the line ("%s") and because \
no valid diffraction data was found in this \
line.""" % (filename,linenumber,currentline,string) )
            
    return allDiffractionFiles


def expandDataFile(string,filename='',linenumber=-1,currentline=''):
    """ Takes in a string which is a list of files and folders.
        It then expands this string into a list of files as follows.
        Any of the files are put into the list. Any of the folders
        
        An exception is raised if some of the items that are given 
        are not files or folders. An exception will be raised if
        any of the files that are given do not have a standard
        file extension. An exception will be raised if the final
        list does not have any files in it.

        filename, linenumber, and currentline are used to format 
        nice exceptions but are all optional... """

    # split the string into a list of file and folder names
    try:
        allDiffractionFilesOrDirectories = \
                General.splitPaths(string)
    except UserInputException:
        raise UserInputException("""%s is not a valid macro \
file because line %d ("%s") is followed by "%s" which can \
not be parsed into a list of files and \
folders.""" % (filename,linenumber,currentline,string) )
        

    allDiffractionFiles = []

    # loop over all the files or folders
    # an error would have been preivously 
    # been raised unless everything in the
    # list is a file or folder.
    for file in allDiffractionFilesOrDirectories:

        if os.path.isdir(file):
            # get all the items in each folder
            dir = General.getallfileswithextensions(file,allExtensions)
            for another in dir:
                allDiffractionFiles.append(
                        "\t"+os.path.join(file,another))
        else:
            # put all the files given to the macro direclty
            # into the list of files
            extension = General.getextension(file)
            if extension in allExtensions:
                allDiffractionFiles.append("\t"+file)
            else:
                # if the given file is of a bad extension,
                # raise an error
                raise UserInputException("""%s is not a valid \
macro file because line %d ("%s") is followed by "%s" which \
contains the file %s which does not have a recognizable \
extension.""" % (filename,linenumber,currentline,string,file) )

    # if no files were found (either in one of the 
    # folders or given explicilty to the program
    # in the macro, then raise an error
    if len(allDiffractionFiles) < 1:
        raise UserInputException("""%s is not a valid macro file \
because line %d ("%s") is followed by "%s" and no diffraction files \
can be found in this string or in folders that are given in this \
string""" % (filename,linenumber,currentline,string) )
        
    return allDiffractionFiles


def test():
    import doctest
    import MacroMode
    doctest.testmod(MacroMode,verbose=0)
    
if __name__ == "__main__":
    test()		
