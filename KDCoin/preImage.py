import hashlib
import random
import time
# from Exercises.week1.helperFunctions import simpleLOD


characters = 'abcdefghijklmnopqrstuvwxyz'
numbers = '1234567890'
charUpper = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

fullCharList = characters + numbers


def generateRandomByteStrings(_length):
    toReturn = ""
    for i in range(random.randint(1, _length)):
        choice = random.choice(fullCharList)
        toReturn += choice
    return bytes(toReturn.encode())


def getDigest(message):
    m = hashlib.sha256()
    m.update(message)
    return m.hexdigest()


def findCollision(numberOfBits, message):
    print("Received:", message)
    starttime = time.time()

    stringsDone = { message:1 }  # keep a list of strings already checked
    number = numberOfBits/8

    toCompare = getDigest(message)[0:int(number)]

    print("looking for", toCompare, "...")

    randomString = generateRandomByteStrings(100)

    while True:
        while randomString in stringsDone:
            randomString = generateRandomByteStrings(100)

        if getDigest(randomString)[0:int(number)] == toCompare:
            print("Found", randomString)
            print("with bytes", getDigest(randomString)[0:int(number)])
            break
        stringsDone[randomString] = 1

    # end
    endtime = time.time()
    print("Total time taken:", endtime-starttime)

    return endtime - starttime


# Find preimage given target text and current digest of the header
def findPreimage(_target, _message, _found, _interrupt):
    strings_done = {}  # keep a hashmap of strings already done

    random_string = generateRandomByteStrings(100)

    while True:
        if not _interrupt.empty():
            print("Interrupted")
            _interrupt.get()
            return ""

        # generate until a new string not tried before has been found
        while random_string in strings_done:
            random_string = generateRandomByteStrings(100)

        if int(getDigest(_message.encode() + random_string), 16) <= _target:
            break
        strings_done[random_string] = 1

    _found.put(random_string.decode())


# if __name__ == '__main__':
#     print(findPreimage(simpleLOD(4), "ThisIsASampleMessage".encode()))
