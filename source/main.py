import sys

##testing commits after merge. had to break everything




def print_usage():
	print "\nUsage:\n--main.py <torrent_file_name.torrent>"
	print "--To create .torrent file, call init_torrent.py <file_name>"

def main():
	args = sys.argv[1:]
	#todo add checking for correct argument input
	if '--help' in args or len(args)==0:
		print_usage()
		sys.exit(2)

##program start
if __name__ == "__main__":
	main()
