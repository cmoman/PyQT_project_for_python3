#!/usr/bin/env python3

import bisect
import gzip
import PyQt4.QtCore as QtCore
import PyQt4.QtGui as QtGui
import PyQt4.QtXml as QtXml

CODEC = "utf-8"
NEWPARA = chr(0x2029)
NEWLINE = chr(0x2028)
DATEFORMAT = "ddd MMM d, yyyy"

def encodeNewlines(text):
    return text.replace("\n\n", NEWPARA).replace("\n", NEWLINE)

def decodedNewlines(text):
    return text.replace(NEWPARA, "\n\n").replace(NEWLINE, "\n")

class Movie(object):
    UNKNOWNYEAR = 1890
    UNKNOWNMINUTES=0
    
    def __init__(self, title=None, year=UNKNOWNYEAR, minutes = UNKNOWNMINUTES, acquired=None, location=None, notes=None):
        self.title = title
        self.year = year
        self.minutes = minutes
        self.acquired =(acquired if acquired is not None
                       else QtCore.QDate.currentDate())
        self.location = location
        self.notes = notes
        
class MovieContainer(object):
    MAGIC_NUMBER = 0x3051E
    OLD_FILE_VERSION = 100
    FILE_VERSION = 101


    def __init__(self):
        self.__fname = ""
        self.__movies = []
        self.__movieFromId = {}
        self.__dirty = False
        
    def key(self, title, year): # new method
        text = title.lower() # converts it all to lower case to simplify the following
        if text.startswith("a "):
            text = text[2:] # removes first two characters
        if text.startswith("an "):
            text = text[3:]
        if text.startswith("the "):
            text = text[4:]
        parts = text.split(" ",1) # this must return a list of words
        if parts[0].isdigit():
            text = "{0:08d}".format(int(parts[0])) #turns the number into an 8 character string with padded zeros
            if len(parts)>1:
                text +=part[1]
        return "{}\t{}".format(text.replace(" ",""), year)
    
    def isDirty(self):
        return self.__dirty # not sure why this is double underscore
    
    
    def setDirty(self, dirty=True):
        self.__dirty=dirty
        
    def movieFromId(self, id):
        return self.__movieFromId[id]  #this is dictionary created using id as the key.
    
    def movieAtIndex(self, index):
        """return the movie based on numerical order"""
        """well it will return the second item in"""
        ''' my guess is that movie will be like a dictionary , the key being the id. the [1] will be the title'''
        return self.__movies[index][1] # this is list containing the movies. what will [1] contain
    
    def add(self, movie):
        if id(movie) in self.__movieFromId:
            return False # prevents the movies being added twice
        key = self.key(movie.title, movie.year)
        bisect.insort_left(self.__movies, [key, movie]) # list or lists
        self.__movieFromId[id(movie)]=movie #dictionary or movie objects
        self.__dirty = True
        return True
        
    def delete(self, movie):
        if id(movie) not in self.__movieFromId:
            return False
        key = self.key(movie.title, movie.year)
        i = bisect.bisect_left(self.__movies, [key, movie])
        del self.__movies[i]
        del self.__movieFromId[id(movie}]
        self.__dirty = True
        return True
        
    def __iter__(self): #reimplement method
        for pair in iter(self.__movies):
            yeild pair[1]
    
    def __len__(self): # reimplement method
        return len(self.__movies):
            
    def setFilename(self, fname): # could we use the @property decorator for the following two.
        self.__fname = fname
        
    def filename(self):
        return self.__fname
        
    @staticmethod
    def formats():
        return "*.mqb"
    
    def save(self, fname=""):
        if fname:
            self.__fname = fname
        if self.__fname.endswith(".mqb"):
            #self.saveQDataStream() could also be another way of doing it.
            return self.saveQDataStream() # so you can actually just it to call another method
        return False, "Failed to save:invalid file extension"
    
    def load(self, fname=""):
        if fname:
            self.__fname = fname
        if self.__fname.endswith(".mqb"):
            return self.loadQDataStream()
        
    def saveQDataStream(self):
        error = None
        file = None
        
        try:
            file= QtCore.QFile(self.__fname)
            if not file.open(QtCore.QIODevice.WriteOnly):
                raise IOError(file.errorString())
            
            stream = QtCore.QDataStream(file)
            stream.writeInt32(MovieContainer.MAGIC_NUMBER) # This is a class variable - not an instance variable
            stream.writeInt32(MovieContainer.FILE_VERSION)
            stream.setVersion(QtCore.QDataStream.Qt_4_8)
            
            for key, movie in self.__movies:
                stream.writeQString(movie.title)
                stream.writeInt16(movie.year)
                stream.writeInt16(movie.minutes)
                stream.writeQString(movie.acquired.toString(QtCore.Qt.ISODate))
                stream.writeQString(movie.location)
                stream.writeQString(movie.notes)
        except EnvironmentError as e:
            error = "Failed to save: {}".format(e)
            
        finally:
            if file is not None:
                file.close()
            if error is not None:
                return False, error
            self.__dirty = False
            return True, " Save {} movie recrods ot{}". format(len(self.__movies),QtCore.QFileInfo(self.__fname).fileName())
        
        def loadQDataStream(self):
            error = None
            file = None
            try:
                file = QtCore.QFile(self.__fname)
                if not file.open(QtCore.QIODevice.ReadOnly):
                    raise IOError(file.errorString())
                stream = QtCore.QDataStream(file)
                magic = stream.readInt32() # read the first integer
                if magic != MovieContainer.MAGIC_NUMBER:
                    raise IOError("unrecognised file type")
                version = stream.readInt32() # read the second integer
                if version < MovieContainer.OLD_FILE_VERSION:
                    raise IOError(" new and unreadable file format")
                new = (False if version == MovieContainer.OLD_FILE_VERSION else True)
                stream.setVersion(QtCore.QDataStream.qt_4_8)
                self.clear(False)
                while not stream.atEnd():
                    title = stream.readQString()
                    year = stream.readInt16()
                    minutes = stream.readInt16()
                    acquired = QtCore.QDate.fromString(stream.readQString(), QtCore.Qt.ISODate)
                    location = ""
                    if new:
                        location = stream.readQString()
                        
                    notes = stream.readQString()
                    self.add(Movie(title, year, minutes, acquired, location, notes))
                except EnvironmentError as e:
                    error = "Failed to load: {}",format(e)
                finally::
                    if file is not None:
                        file.close()
                    if error is not None:
                        return False, error
                    self.__dirty = False
                return True, "Loaded {0} movie records from {1}",format(
                    len(self.__movies),
                    QtCore.QFileInfo(self.__fname).fileName())
            
            def exportXml(self, fname):
                error = None
                fh = None
                try:
                    fh = QtCore.QFile(fname)
                    if not fh.open(QtCore.QIODevice.WriteOnly):
                        raise IOError(fh.errorString())
                    stream = QtCore.QTextStream(fh)
                    stream.setCodec(CODEC)
                    stream << ("<?xml version = '1.0' encoding='{0}'?>\n"
                               "<!DOCTYPE MOVIES>\n"
                               "<MOVIES VERSION='1.0'>\n".format(CODEC)) # this line basically does the heading of the xml file
                    for key, movie in self.__movies:
                        stream << ("MOVIE YEAR='{0]' MINUTES = '{1}'"
                                   "ACQUIRED = '{3}'>\n".format(movie.year,
                                                                movie.minutes,
                                                                movie.acquired.toString(QtCore.Qt.ISODate)))\
                            << "<TITLE>" << movie.title.toHtmlEscaped() \ 
                            << "</TITLE>\n" << "<LOCATION>" # toHtmlEscaped() used instead of 
                        
                        
                        
                    
                    
                                  
                
                
                
             
        
            
        
        
        
class SaxMovieHandler(QtXml.QXmlDefaultHandler):

    def __init__(self, movies):
        super().__init__()
        self.movies = movies
        self.text = ""
        self.error = None
        
    def clear(self): # this seems to be a new method
        self.year = None
        self.minutes = None
        self.acquired = None
        self.title = None
        self.location =""
        self.notes = None
    
    def startElement(self,namespaceURI,localName,qName,attributes): # reimplement method
        self.clear()
        self.year = int(attributes.value("YEAR"))
        self.minutes = int(attributes.value("MINUTES"))
        ymd = attributes.value("ACQUIRED").split("-")
        
        
    def endElement(self,namespaceURI,localName,qName): # reimplement method
        pass
        
    def fatalError(self, exception): # reimplement method
                           
    
        