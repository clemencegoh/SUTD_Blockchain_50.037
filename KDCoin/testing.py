import re


def extractFromText(_text):
    pattern = re.compile("Public Key: (.*)<br>Private Key: (.*)<br>")
    match = pattern.match(_text)
    print(match.group(1))
    print(match.group(2))


if __name__ == '__main__':
    extractFromText("Public Key: 5a3d7c8a584bffc708ca2c665759a3e3d25014a9a85ff589cfb23aece445df8f"
                    "bc2b266036df58bde6270db7f6a31305<br>Private Key: e658fc826e29404e039df06735e1"
                    "cc6fa2ec8c48f771d169<br>Please save these 2 (They are unrecoverable)"
                    "<!DOCTYPE html>")
