#!/usr/bin/env pytho
from gmusicapi import Mobileclient
import getpass

class Song:
    song_length = 25
    artist_length = 25

    def __init__(self,  song_id, name, artist, hype):
        self.song_id = song_id
        self.name = name
        self.artist = artist
        self.hype = hype

    def modified_name_length(self):
        res = self.name[:self.song_length]
        if len(res) < self.song_length:
            res += ' ' * (self.song_length - len(res))
        return res

    def modified_artist_length(self):
        res = self.artist[:self.artist_length]
        if len(res) < self.artist_length:
            res += ' ' * (self.artist_length - len(res))
        return res

    def to_string(self, print_id = True):
        if print_id:
            return self.song_id + "\t" + self.modified_name_length() + "\t" + self.modified_artist_length() + '\t' + str(self.hype) + '\n'
        else:
            return self.modified_name_length() + "\t" + self.modified_artist_length() + '\t' + str(self.hype) + '\n'





class MusicEditor:

    def __init__(self):
        print("Welcome to the Music Library! ")

        print("Connecting to Google API...")
        self.api = Mobileclient()
        self.api.login(raw_input("Gmail Address: "), getpass.getpass('Password: '), Mobileclient.FROM_MAC_ADDRESS)


        print("Logged on!")

        self.file_reader = open("song_list.txt", "r")
        self.library = self.api.get_all_songs()
        self.running = True

    def init_list_of_songs(self):
        self.list_of_songs = self.update_library()
        self.file_reader.close()
        print("Ready to use!")


    def parse_line(self, line):
        return line.split('\t')

    def write_to_doc(self, file_writer):
        print("Writing to Document...")
        for song in self.list_of_songs:
            #Each file has the following: id \t name \t artist \t hype_level
            file_writer.write(song.song_id +
            '\t' + song.name +
            '\t' + song.artist+
            '\t' + str(song.hype) + '\n')
        print("Finished Writing to Document!")

    # library: The library recieved from Google api
    # file_writer: The file where the songs are recorded
    # list_of_songs: The dictionary we made
    def update_library(self):
        print("Setting up libraries...")
        temp_dict = {}
        map_of_songs = {}
        res = []

        # Takes the document and gets the list of songs
        for doc_line in self.file_reader.readlines():
            song_ar = self.parse_line(doc_line)
            map_of_songs[song_ar[0]] = Song(song_ar[0], song_ar[1], song_ar[2], int(song_ar[3]))

        # Takes the tracks from Google and Adds Songs to list_of_songs
        # Also takes items from the library and puts them in temp_dict
        for track in self.library:
            temp_dict[track['id']] = True
            if(track['id'] not in map_of_songs):
                map_of_songs[track['id']] = Song(track['id'],track['title'].encode('ascii', 'replace'), track['artist'].encode('ascii', 'replace'), 0)

        # Takes the list_of_songs and deletes items not in the original file
        return [value for key, value in map_of_songs.iteritems() if (key in temp_dict)]





    def index_maker(self, index):
        str_index = '['+str(index)+']'
        if (len(str_index) <6):
            str_index+= ' '*(6 - len(str_index))
        return str_index+'\t'
    def quit(self):
        self.running = False
        return "Ending Program..."

    def pong(self):
        return "pong"
    def enter(self):
        return '>>'
    def song_line(self, song, index):
        return self.index_maker(index)+song.to_string(False)
    def print_song_list(self):
        res = "########################################### List ###########################################\n"
        for index, song in enumerate(self.list_of_songs):
            res += self.song_line(song, index)
        return res

    def sort_song_list(self):
        text = raw_input("Sort by (name, artist, hype): \n>> ").strip()
        res = {
            'name' : sorted(self.list_of_songs, key=(lambda x: x.name)),
            'artist' : sorted(self.list_of_songs, key=(lambda x: x.artist)),
            'hype' : sorted(self.list_of_songs, key=(lambda x: x.hype))

        }.get(text, self.list_of_songs)
        self.list_of_songs = res
        return self.print_song_list()

    def set_hype_level(self, index, level):
        self.list_of_songs[index].hype = level
        return self.list_of_songs[index].name + " has a hype level of "+ str(level)

    def inithype(self):
        for index, song in enumerate(self.list_of_songs):
            print(self.song_line(song, index))
            text = raw_input("Hype Rating: \n>>").strip()
            if(text == ":exit"): break
            try:
                self.list_of_songs[index].hype = int(text)
            except ValueError:
                print("Not a valid input, skipped...")

        return "Finished Classfying Hype!"



    def set_level(self):
        text = raw_input("Set (hype) [index] [level]: \n>>").strip()
        text_ar = text.split(' ')

        try:
            return {
                'hype' : self.set_hype_level(int(text_ar[1]), int(text_ar[2]))
            }.get(text_ar[0], "No such field exists. ")
        except ValueError:
            return "Not a valid input. 2nd and 3rd fields must be integers"
        except IndexError:
            return "Not a valid input. Need 3 fields"

    def create_playlist(self):

        try:
            min_hype = int(raw_input("Minimum level of Hype\n>>").strip())
            max_hype = int(raw_input("Maximum level of Hype\n>>").strip())
            playlist_id = self.api.create_playlist("Hype Music Level: "+str(min_hype)+" - "+str(max_hype))
            track_list = [song.song_id for song in self.list_of_songs if(song.hype >= min_hype and song.hype <=max_hype)]

            self.api.add_songs_to_playlist(playlist_id, track_list)

            return "Playllist created!"

        except ValueError:
            return "Sorry, not an int. Try again"




    match_options = {
        ':quit' : quit,
        'quit' : quit,
        'exit' : quit,
        '' : enter,
        'ping' : pong,
        'print' : print_song_list,
        'sort' : sort_song_list,
        'set' : set_level,
        'inithype': inithype,
        'create_playlist': create_playlist

    }


    def match(self, x):
        try:
            return self.match_options[x](self)
        except KeyError:
            return "Invalid Input, please try again..."

    def run(self):

        self.init_list_of_songs()

        while(self.running):
            text = raw_input(">> ").strip()
            print(self.match(text))

        file_writer = open("song_list.txt", "w")
        self.write_to_doc(file_writer)

        file_writer.close()
        print('Closing...')


## SCRIPT CALL

me = MusicEditor()
me.run()


    #hype_track_ids = [track['id'] for track in library if raw_input("is "+track['title'].encode('utf8')+" hype?\n") == "1"]
    #playlist_id = api.create_playlist('Hype Music')
    #api.add_songs_to_playlist(playlist_id, hype_track_ids)


    #sweet_track_ids = [track['id'] for track in library
    #                   if track['artist'] == 'Ariana Grande']
    #
    #playlist_id = api.create_playlist('Rad muzak')
    #api.add_songs_to_playlist(playlist_id, sweet_track_ids)
