from tkinter import *

root = Tk()

def stopFunc():
	print("Stop")
	exec(open('stop.py').read())

def forwardFunc():
    print("forward")
    exec(open('forward.py').read()) #write any file with .py extension.This method is similar to rightclick and open

def leftFunc():
    print("left")
    exec(open('left.py').read())

def rightFunc():
    print("right")
    exec(open('right.py').read())

def reverseFunc():
    print("reverse")
    exec(open('reverse.py').read())

def forwardSonarFunc():
    print("forward sonar")
    exec(open('forwardSecurity.py').read())

def leftSonarFunc():
    print("left sonar")
    exec(open('leftSecurity.py').read())

def rightSonarFunc():
    print("right sonar")
    exec(open('rightSecurity.py').read())

def autopilotFunc():
    print("autopilot")
    exec(open('autopilot.py').read())
    
def exitFunc():
	print("Stop")
	exec(open('exit.py').read())

stopButt = Button(root, text = "stop", command = stopFunc)
stopButt.pack()
forwardButt = Button(root, text = "forward", command = forwardFunc)
forwardButt.pack()
leftButt = Button(root, text = "left", command = leftFunc)
leftButt.pack()
rightButt = Button(root, text = "right", command = rightFunc)
rightButt.pack()
reverseButt = Button(root, text = "reverse", command = reverseFunc)
reverseButt.pack()
forwardSonarButt = Button(root, text = "sonar forward", command = forwardSonarFunc)
forwardSonarButt.pack()
leftSonarButt = Button(root, text = "sonar left", command = leftSonarFunc)
leftSonarButt.pack()
rightSonarButt = Button(root, text = "sonar right", command = rightSonarFunc)
rightSonarButt.pack()
autopilotButt = Button(root, text = "autopilot", command = autopilotFunc)
autopilotButt.pack()
exitButt = Button(root, text = "exit", command = exitFunc)
exitButt.pack()

root.mainloop()