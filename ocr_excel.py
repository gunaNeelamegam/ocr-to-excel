from PIL import Image
import pytesseract
import numpy as np
from pytesseract import Output
from typing import List, Union
import data
import time


def getCompanyName(content):
    sample = ""
    for data1 in content[0].values():
        printPad("Company Name ....")
        for i, data in enumerate(data1):
            if "<_" not in str(data).strip():
                sample += data
            else:
                return (sample, data1[i + 1 :])


def getCountry(content):
    for word in content:
        if word.lower() in [*data.allCountries()]:
            printPad(word.lower())
            return word.lower()


def getName(content):
    sample = ""
    for i, word in enumerate(content):
        if "#" not in word:
            sample += word
            printPad(f"{sample=}")
        else:
            return (sample, content[i:])


def getEmail(content):
    samples = []
    for word in content:
        if "@" in word:
            printPad(word)
            samples.append(word)
    return samples


def getAddress(content):
    samples = ""
    for word in content:
        if "-" not in word:
            samples += word
        else:
            return samples


def printPad(message):
    return print("#" * 20, message, "#" * 20)


def getCity(content):
    districts = []
    for state in data.samples.get("states"):
        districts = [*districts, *state.get("districts")]

    for word in content:
        if word in districts:
            printPad(word)
            return word


def getNumber(data):
    starting_index = None
    ending_index = None
    i = "".join(data).rfind("@")
    if i != -1:
        ending_index = i
    index = "".join(data).find("+")
    printPad("".join(data)[index:index+13])
    if index != -1:
        starting_index = index
    sample="".join(data)[index:index+13]
    return sample


import csv


def filter_and_append_to_csv(data):
    filtered_data = {
        "email": "",
        "name": "",
        "fullName": "",
        "phoneNumber": "",
        "Address": "",
        "Country": "",
        "City": "",
        "secondaryEmail": "",
        "secondaryNumber": "",
        "companyName": "",
    }
    filtered_data["companyName"], newData = getCompanyName(data)
    filtered_data["name"], newData = getName(newData)
    filtered_data["fullName"] = filtered_data["name"]
    filtered_data["Address"] = getAddress(newData)
    filtered_data["City"] = getCity(newData)
    filtered_data["Country"] = getCountry(newData)
    if emails := getEmail(newData):
        if len(emails) > 1:
            filtered_data["email"] = emails[0]
            filtered_data["secondaryEmail"] = emails[1:].join(",")
        else:
            filtered_data["email"] = emails[0]
    
        filtered_data["phoneNumber"] = getNumber(newData)

    with open("sample.csv", "w+") as fp:
        w = csv.DictWriter(fp, filtered_data.keys())
        w.writeheader()
        w.writerows([dict(filtered_data)])


def image_to_text(file_name: list) -> list:
    data = []
    for file in file_name:
        img = np.array(Image.open(file))
        text = pytesseract.image_to_data(img, output_type=Output.DICT)
        if content := text["text"]:
            data.append(
                {
                    file: [
                        *filter(
                            None,
                            map(lambda line: str(line).strip(), filter(None, content)),
                        )
                    ]
                }
            )
            filter_and_append_to_csv(data)
    return data


import os

image_to_text([file for file in os.listdir(os.path.curdir) if ".jpg" in file])
