import os, threading, time, subprocess
from HubPairer import HubPairer


MY_HUB_ID = "2"


HubPairerInst = HubPairer(MY_HUB_ID)

HubPairerInst.pairAndStreamAudio("1")
