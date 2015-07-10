#!/usr/bin/python

import os
import errno
import sys
import shutil
import optparse
import datetime
import hachoir_parser
import hachoir_metadata

from PIL import Image
from hachoir_core.error import HachoirError
from hachoir_core.cmd_line import unicodeFilename
from hachoir_core.tools import makePrintable
from hachoir_core.i18n import getTerminalCharset
from commands import *

def makeJpegPath(jpegfn):
    basename = os.path.basename(jpegfn).replace(" ", "_")
    retVal = os.path.join("unknown", "unknown", basename)
    try:
        im = Image.open(jpegfn)
        if hasattr(im, '_getexif'):
            exifdata = im._getexif()
            if exifdata is not None:
                ctime = exifdata.get(0x9003, None)
                if ctime is not None:
                    dt = datetime.datetime.strptime(ctime, "%Y:%m:%d %H:%M:%S")
                    retVal = os.path.join(dt.strftime("%Y"), dt.strftime("%Y-%m-%d"), basename)
    except:
        pass
    
    return retVal

def makeMovPath(filename):
    basename = os.path.basename(filename).replace(" ", "_")
    retVal = os.path.join("unknown", "unknown", basename)
    try:
        filename, realname = unicodeFilename(filename), filename
        parser = hachoir_parser.createParser(filename, realname)
        if not parser:
            return retVal
        metadata = hachoir_metadata.extractMetadata(parser)
        if not metadata:
            return retVal

        creationDate = metadata.getItem("creation_date", 0)

        if creationDate is not None and creationDate.value is not None:
            retVal = os.path.join(creationDate.value.strftime("%Y"), creationDate.value.strftime("%Y-%m-%d"), basename)
    
    except HachoirError, err:
        pass

    return retVal

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

def main():
    parser = optparse.OptionParser()
    parser.add_option("-s", "--source", dest="source", help="directory to read photos", metavar="FILE")
    parser.add_option("-d", "--destination", dest="destination", help="directory to write photos", metavar="FILE")
    (options, args) = parser.parse_args()

    for r,d,f in os.walk(options.source):
        for files in f:
            sourceFile = os.path.join(r,files)
            destinationFile = None
            ext = os.path.splitext(files)[1].lower()

            if ext in [ ".mov", ".avi", ".3gp", ".mp4" ]:
                 destinationFile = os.path.join(options.destination, makeMovPath(sourceFile))
            if ext in [ ".jpg", ".jpeg" ]:
                 destinationFile = os.path.join(options.destination, makeJpegPath(sourceFile))

            if destinationFile != None:
                if (not os.path.isfile(destinationFile)) or os.path.getsize(sourceFile) != os.path.getsize(destinationFile):
                    print sourceFile, " copy ", destinationFile
                    mkdir_p(os.path.dirname(destinationFile))
                    shutil.copy2(sourceFile, destinationFile);
                else:
                    print sourceFile, " skip ", destinationFile

if __name__ == "__main__":
    main()
