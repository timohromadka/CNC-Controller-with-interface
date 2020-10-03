import PySimpleGUI as sg
import createGCode as cgc
import os
import feedback as fb
import camera_capture as cc

# DEFINE LANGUAGE FOLDER

def updateWindow(oldLayoutNum, newLayoutNum):
    window[f'-COL{oldLayoutNum}-'].update(visible=False)
    window[f'-COL{newLayoutNum}-'].update(visible=True)

"""
Read the lines from the respective .txt file 
NO UNICODE CHARACTERS ALLOWED
@param fileName
"""
def updateLanguage(fileName):
    try:
        file = 'language_folder/%s' % fileName
    except FileNotFoundError:
        sg.popup_error("language_folder/%s missing" % fileName)
        return
    with open(file) as f:
        for cnt, line in enumerate(f):
            window.Element('text%d' % cnt).Update(line)

def typeCheck():
    try:
        file = 'language_folder/input_types.txt'
    except FileNotFoundError:
        sg.popup_error('language_folder/input_types.txt missing')
        return
    with open(file) as f:
        for cnt, line in enumerate(f):
            line = "".join(line.split()) # remove all whitespaces from line read
            try:
                user_input = values['input%d' % cnt]
            except KeyError:
                return None  # finished all inputs, no additional input found
            if user_input == None:
                return "please enter a value at line #%d" % cnt+1
            if line == "float":
                try:
                    testVal = float(user_input)  # try casting to float
                except ValueError:
                    return "at input #%d: can't convert %s to %s" % (cnt+1, user_input, line)  # cnt + 1 to not start from 0
            elif line == 'path':
                if not os.path.isdir(user_input):
                    return "at line #%d: please enter a valid folder path \nerror at '%s'" % (cnt+1, user_input)
        return None  # no errors found

def openFile(fileName):
    try:
        file = 'language_folder/%s' % fileName
    except:
        print("Couldn't find language file")
    return file

# ----------- Create the first 'select language' layout -----------
language_layout = [
    [sg.Text('Select Language:', size=(20,1), font=("Helvetica", 20))],
    [sg.Combo(('English', 'Slovenčina', 'Deutsch'), enable_events=True, key='language_combo', size=(20, 3))]]

# create specific layouts with different languages
user_layout = [[sg.Text('Slider + Image Stitcher', size=(20, 1), font=("Helvetica", 20))],
    [sg.Text("- - -", size=(45, 1), key='text0')],
    [sg.InputText('(e.g. 40)', size=(35, 1), key='input0')],
    [sg.Text("- - -", size=(45, 1), key='text1')],
    [sg.InputText('width (cm)', size=(10, 1), key='input1'), sg.Text("x", size=(1, 1)), sg.InputText('height (cm)', size=(10, 1), key='input2')],
    [sg.Text("- - -", size=(45, 1), key='text2')],
    [sg.InputText('width (cm)', size=(10, 1), key='input3'), sg.Text("x", size=(1, 1)), sg.InputText('height (cm)', size=(10, 1), key='input4')],
    [sg.Text("- - -", size=(45, 1), key='text3')],
    [sg.InputText("e.g. 8, 12", size=(35, 1), key='input5')],
    [sg.Text("- - -", size=(45, 1), key='text4')],
    [sg.InputText('4', size=(5, 1), key='input6'), sg.Text(":", size=(1, 1)), sg.InputText('3', size=(5, 1), key='input7')],
    [sg.Text("- - -", size=(45, 1), key='text5')],
    [sg.InputText("e.g. 5000", size=(35, 1), key='input8')],
    [sg.Text("- - -", size=(45, 1), key='text6')],
    [sg.InputText("25", size=(35, 1), key='input9'), sg.Text("%", size=(3, 1))],
    [sg.Text("- - -", size=(45, 1), key='text7')],
    [sg.InputText('Select folder', size=(35, 1), key='input10'), sg.FolderBrowse()],
    [sg.Text("- - -", size=(45, 1), key='text8')],
    [sg.InputText('Select folder', size=(35, 1), key='input11'), sg.FolderBrowse()],
    [sg.Text("- - -", size=(45, 1), key='text9')],
    [sg.InputText(size=(35, 1), default_text='output', key='input12'), sg.Text(".png", size=(4, 1))],
    [sg.Text("- - -", size=(45, 1), key='text10')],
    [sg.InputText('Select folder', size=(35, 1), key='input13'), sg.FolderBrowse()],
    ]

layout = [
    [sg.Column(language_layout, key='-COL0-')],
    [sg.Column(user_layout, visible=True, key='-COL1-')],
    [sg.Button('<---', disabled=True), sg.Button('--->'), sg.Button('Exit'), sg.Button('START', visible=False, button_color=('white', 'cyan'), size=(10,3), key='start_button'),
     sg.Button('Next', button_color=('white', 'green'), size=(10, 1), visible=False, key='next_button')]]

window = sg.Window('CNC gcode', layout)

language = 0 # 1-english, 2-slovak, 3-german
while True:
    event, values = window.read()
    if event in (None, 'Exit'):
        break

    if event == '<---':
        window[f'-COL0-'].update(visible=True)  # error message
        window.Element('<---').update(disabled=True)
        window.Element('--->').update(disabled=False)
        window.Element('next_button').update(disabled=False)
    elif event == '--->':
        window.Element('--->').update(disabled=True)
        window.Element('<---').update(disabled=False)
        # record selected language
        combo_value = values['language_combo']
        if combo_value != '':
            # make next button visible
            window.Element('next_button').update(visible=True)
            if combo_value == 'English':
                updateLanguage('en.txt')
                language=1
            elif combo_value == 'Slovenčina':
                updateLanguage('sk.txt')
                language=2
            elif combo_value == 'Deutsch':
                updateLanguage('de.txt')
                language=3
            updateWindow(0, 1)
            layout_num = 1 # user layout, not the language layout
    elif event == 'next_button':
        error_message = typeCheck() # None if no errors, else a string containing error message
        if error_message != None: # error somewhere
            window[f'-COL0-'].update(visible=False)
            window[f'-COL1-'].update(visible=True)
            sg.popup_error(error_message)
        else:
            window[f'-COL1-'].update(visible=False)

            # process all information
            targetMegapixels = float(values['input0'])
            paintingCMWidth, paintingCMHeight = int(values['input1']), int(values['input2'])
            camCMWidth, camCMHeight = int(values['input3']), int(values['input4'])
            camMegapixels = float(values['input5'])
            camRatio = int(values['input6']), int(values['input7'])
            pauseDuration = int(values['input8'])
            minOverlap = int(values['input9'])
            imageStitchFolder = values['input10']
            outputImageFolder = values['input11']
            outputImageName = values['input12']
            gCodeFolder = values['input13']
            xAmount, yAmount = fb.calculateMinimumOverlap(camCMWidth, camCMHeight, paintingCMWidth, paintingCMHeight, minOverlap)

            display, canProceed = fb.giveFeedback(language, targetMegapixels, (paintingCMWidth, paintingCMHeight), (camCMWidth, camCMHeight), camMegapixels, camRatio, xAmount, yAmount)
            sg.popup_ok(display)

            if canProceed:
                window.Element('start_button').Update(visible=True)

                finalXAmt, finalYAmt, xStep, yStep, xLeft, yDown = \
                    cgc.calculateGCode(targetMegapixels, (paintingCMWidth, paintingCMHeight), (camCMWidth, camCMHeight), camMegapixels, camRatio, pauseDuration, minOverlap, gCodeFolder)

            window.Element('next_button').update(disabled=True)
    elif event == 'start_button':
        cc.cameraCapture(imageStitchFolder, xAmount, yAmount, xStep, yStep, xLeft, yDown, pauseDuration)


window.close()

typeCheck()