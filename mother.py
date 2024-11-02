import os
import json
import requests
from dotenv import load_dotenv

from doubleCheckAgent import PageVerificationAgent

checkAgent = PageVerificationAgent()


def runMother(goal: str):
    goalCompleted = False

    while goalCompleted == False:
        print()