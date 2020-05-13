import re
from collections import Counter
from spellchecker import SpellChecker
from langdetect import detect

class Vigenere:
	# sorry in advance for my horrible taste in picking out variable names.
	# also, I'm scared to estimate O(n).
	
	def __init__(self, encrypted, language="en", kw_max=10, kw_min=3, consonant_cutoff=4):
		# Configurable parameters
		self.MAX_KEYWORD_LENGTH = kw_max #Assumption: key won't be longer than 10 chars
		self.MIN_KEYWORD_LENGTH = kw_min #Assumption: key won't be shorter than 3 chars
		self.CONSONANT_CUTOFF = consonant_cutoff
		self.language = language

		# some global variables, because I'm honestly too lazy to keep passing them around
		self.keylength = 1
		self.wordlist = []
		self.e = ""
		self.spell = SpellChecker(language=language)

		# start the fun
		self.run(encrypted)



	'''
	 __ __    ___  _      ____   ___  ____       _____  __ __  ____     __ ______  ____  ___   ____   _____
	|  |  |  /  _]| |    |    \ /  _]|    \     |     ||  |  ||    \   /  ]      ||    |/   \ |    \ / ___/
	|  |  | /  [_ | |    |  o  )  [_ |  D  )    |   __||  |  ||  _  | /  /|      | |  ||     ||  _  (   \_ 
	|  _  ||    _]| |___ |   _/    _]|    /     |  |_  |  |  ||  |  |/  / |_|  |_| |  ||  O  ||  |  |\__  |
	|  |  ||   [_ |     ||  | |   [_ |    \     |   _] |  :  ||  |  /   \_  |  |   |  ||     ||  |  |/  \ |
	|  |  ||     ||     ||  | |     ||  .  \    |  |   |     ||  |  \     | |  |   |  ||     ||  |  |\    |
	|__|__||_____||_____||__| |_____||__|\_|    |__|    \__,_||__|__|\____| |__|  |____|\___/ |__|__| \___|
																										   
	'''


	# I think this technically counts as multi-language-support AND easy future scaling compatibility...?
	def get_most_common_chars(self):
		# such options, much wow...
		# lazy does the trick for now.
		if self.language == "de":
			return ["E", "N", "R", "I", "S", "T", "A", "D", "H"]
		else:
			return ["E", "T", "A", "O", "I", "N", "S", "H", "R"]


	# check if the word meets the CONSONANT_CUTOFF. Easy enough.
	def vowel_word(self, word):
		vowels = ["A", "E", "I", "O", "U"]
		streak = 0
		for c in word:
			if streak > self.CONSONANT_CUTOFF: return False
			if c in vowels: streak = 0
			else: streak += 1
		return streak < self.CONSONANT_CUTOFF

	# analogous to using a Vigenere look-up table
	def decrypt_char(self, e, k):
		return chr(65 + (ord(e)-ord(k))%26)

	# redundant, but makes it clear what the function can be used for
	def get_encrypt_key(self, e, d):
		return self.decrypt_char(e, d)

	# the fact that python has no built-in function for this is astounding.
	def factors(self, numbers):
		primfac = []
		for n in numbers:			
			d = 2
			while d*d <= n:
				while (n % d) == 0:
					primfac.append(d)
					n //= d
				d += 1
			if n > 1:
			   primfac.append(n)
		return sorted(list(set(primfac)))

	# quick helper function to gather and print all words of wordlist that also are in dictionary
	def print_most_probable(self):
		known = sorted(self.spell.known(self.wordlist))
		print("---  Printing ", len(known), " most probable keywords ---")
		for k in known:
			print(k.upper())

	# take the word, change every letter of the word and replace it with every other letter of the alphabet, respectively
	def mutate_word(self, word):
		mutated = []
		for c in range(len(word)):
			for i in range(1,26):
				mw = list(word)
				mw[c] = chr(((ord(word[c])-65+i)%26)+65) # it works. even though it looks like it shouldn't.
				jmw = "".join(mw)
				mutated += [jmw]
		return mutated



	'''
	 ___ ___   ____  ____  ____       _____  __ __  ____     __ ______  ____  ___   ____   _____
	|   |   | /    ||    ||    \     |     ||  |  ||    \   /  ]      ||    |/   \ |    \ / ___/
	| _   _ ||  o  | |  | |  _  |    |   __||  |  ||  _  | /  /|      | |  ||     ||  _  (   \_ 
	|  \_/  ||     | |  | |  |  |    |  |_  |  |  ||  |  |/  / |_|  |_| |  ||  O  ||  |  |\__  |
	|   |   ||  _  | |  | |  |  |    |   _] |  :  ||  |  /   \_  |  |   |  ||     ||  |  |/  \ |
	|   |   ||  |  | |  | |  |  |    |  |   |     ||  |  \     | |  |   |  ||     ||  |  |\    |
	|___|___||__|__||____||__|__|    |__|    \__,_||__|__|\____| |__|  |____|\___/ |__|__| \___|
																								
	'''


	# figure out the length of the encryption key
	def find_keylength(self):
		kl = {} # store for repeating phrases and their distance in chars
		blacklist = [] # sounds cooler than "already tried these"

		# outer loop: test all lengths of keywords (within parameters set in __init__)
		for i in range(self.MAX_KEYWORD_LENGTH, self.MIN_KEYWORD_LENGTH-1, -1):
			# inner loop: take every letter of the encrypted text as a starting point
			for j in range(0, len(self.e)-i+1):

				# overall, every phrase with length between min/max parameters that the encrypted text contains is examined:
				chunk = self.e[j:j+i]
				if chunk not in blacklist: # save some (miniscule amount of) compute time, and more importantly, make sure there's no need to deal with duplicates
					pat = r'(?<=' + chunk + ').+?(?=' + chunk + ')' # evaluates to a list of all non-overlapping strings between instances of the chunk
					matches = re.findall(pat, self.e)

					# throw out any findings that are longer than the maximum allowed keylength
					# add i to the length of the remaining strings, since the regex only delivered the string between two chunks
					# store in kl if there's still something left to store, blacklist either way.
					results = sorted([len(m)+i for m in matches if len(m)+i <= self.MAX_KEYWORD_LENGTH])
					if results: kl[chunk] = results
					blacklist += [chunk]

		# print a nice overview for the user.
		# figure out the most probable keylength
		# but let user do judgement call, of course
		print ("---  Found following repeating phrases and possible keylengths associated with each: ---")
		lengths_raw = []
		all_primfacs = []
		for k, item in sorted(kl.items(), key=lambda k: len(k), reverse=True):
			print("--- ", k, ": ", item, "->", self.factors(item))
			all_primfacs += self.factors(item)
			lengths_raw += item
			
		print ("---  Frequencies of distances between repeating phrases: ---")
		lengths = reversed(sorted(list(set(lengths_raw))))
		for l in lengths:
			print("--- ", l, ": ", lengths_raw.count(l), "x")

		# suggest user the longest keylength that is a primfactor to all distances in kl
		most_common, count = Counter(reversed(sorted(all_primfacs))).most_common(1)[0]  # 3, 1
		
		choice = input("---  Please enter the keylength or leave blank for recommended length of (" + str(most_common) + "): ")
		keylength = int(choice) if len(choice) else most_common
		print("---  Continuing with keylength ", keylength, " ---")

		# that wasn't too bad, was it? Could sure use some cleaning up though
		return keylength


		

	# figure out combinations of letters that result in the most common letter in each subset of the encrypted text to be
	# translated to som eof the more common letters in the text's language
	def generate_keys(self):
		# split the text into subsets - one for each letter the is ought to have based on the keylength
		subsets = [self.e[i::self.keylength] for i in range(0, self.keylength)]

		keychars = []
		for s in subsets:
			key_options = []
			mc_char = max(set(s), key = s.count) # extract the most common letter in subnet

			# get_most_common_chars() returns a list of just that.
			# we then assume that the most common letter of our subset has to correspond to one of those
			# get_encrypt_key() returns the key that encrypts each of these most common chars to the most common letter of the subset
			# in other words: we figure out all the letters that COULD make up the keyword, ordered by their index in the key
			for mc in self.get_most_common_chars():
				key_options += [self.get_encrypt_key(mc_char, mc)]
			keychars += [key_options]

		# calling a recursive helper funktion
		self.generate_wordlist(keychars, "", 0)
		
		
	# OH, why hast thou forsaken us, GOD of time complexity?
	# Were not once these valleys filled with polynomials?
	# Did thou not promise us log(n)?
	# But alas, ye fell
	# Primordial, O(1)
	# To be devoured
	# As all mortal things must be
	# And henceforth heed grim warning:
	# *Beware the STACK OVERFLOW*
	# -
	# In all serious though, I am open to sggestions. Please.
	
	def generate_wordlist(self, keysoup, word, step):
		# if there's more consonants in a row than the cutoff, it's fair to assume the word is no actual word. Marginal reduction in wordlist-size.
		if step > self.CONSONANT_CUTOFF and not self.vowel_word(word): return
		# reached the last letter - add word to global wordlist
		if step == self.keylength:
			self.wordlist += [word]
		# for every possible letter at position "step", call function recursively
		else:
			for c in keysoup[step]:
				self.generate_wordlist(keysoup, word+c, step+1)
		

	
		

	# present the user with the option to either see every possible keyword in the list
	# or, much more reasonable, only show the ones that belong to the text's language dictionary
	def choose_keyword(self):
		# show list of keywords (either in dictionary or all)
		print("---  Keywordlist contains ", len(self.wordlist), " entries. ---")
		choice = input("---  [1]: show most probable --- [2]: show all --- : ")
		if choice == "2":
			for i in sorted(self.wordlist):
				print(i)
		else:
			self.print_most_probable()

		# get userinput (or not), return it (will then be used to decrypt, or, if no input given, the previously printed list will be used)
		chosen_keyword = input("---  Please enter the keyword you would like to use, or leave blank to try all and filter for most probable: ")
		return chosen_keyword



	

	# with all necessary information gathered (keylength, keywordlist to be used):
	# proceed to decrypt with user given keyword IF ANY,
	# otherwise try the list of probable candidates,
	# or try every one-char mutation of a word,
	# OR try to brute force the keyword ("desperate")
	def decrypt(self, chosen_keyword="", desperate=False, mutatedlist=[]):
		trylist = []
		filtered = True
		counter = 0

		# user did choose a specific keyboard - just try this.
		if len(chosen_keyword):
			trylist = [chosen_keyword]
			filtered = False

		# no single keyword was provided, but a list of a mutated keyword
		elif len(mutatedlist):
			trylist = sorted(mutatedlist)

		# nothing was provided - try most likely based on dictionary
		elif not desperate:
			trylist = sorted(list(self.spell.known(self.wordlist)))

		# brute force the entire wordlist. Fair warning: maaaay take a while.
		else:
			trylist = sorted(self.wordlist)


		for w in trylist:
			decrypt = "" # the decrypted string
			for c in range(len(self.e)):
				decrypt += self.decrypt_char(self.e[c], w[c%self.keylength].upper()) # decrypt letter for letter
			if (filtered and detect(decrypt) == self.language) or not filtered: # if filter ON: only print the relevant reults of the decrypt
				print("---  ", w.upper(), "  --- Trying option ", trylist.index(w)+1, "out of", len(trylist), " possibilities ---")
				print(decrypt)
				print()
				counter += 1

		if filtered: print("--- ", counter, " likely key/cleartext pairs found. ---")

		if not desperate:
			found = input("---  Is the correct key/cleartext pair among the shown? [Y/n]: ") # if Y is entered here, program ends
			if found == "n":
				# offer to try mutations when a decrypted text reads like lots of spelling mistakes, but generally of the desired language
				choice = input("---  If one of the above solutions seems -almost- right, enter it, otherwise leave empty: ") 
				if len(choice):
					mutations = self.mutate_word(choice.upper())
					print("---  Trying", len(mutations), "possible one-char-mutations of \"", choice.upper(), "\" ---")
					self.decrypt(mutatedlist=mutations)
				else:
					# good luck.
					print("---  Trying in desperate mode (bruteforcing", len(self.wordlist), "possibilities, this might take a while... ---")
					self.decrypt(desperate=True)
			else: print("---  End of program ---")
		else: print("---  End of program ---")


	
				

	

	# pretty self-explanatory
	# --- Step 1: Figure out most likely keylength
	# --- Step 2: Generate a list of suitable keys with that length
	# --- Step 3: Either pick a keyword and try it, or try the whole list. Your computer won't mind.
	# --- Step 4: Decrypt the text with the chosen keyword(s). If it worked, yay; if not, try try again?
	def run(self, encrypted):
		self.e = encrypted.upper()
		self.keylength = self.find_keylength()
		self.generate_keys()
		chosen_keyword = self.choose_keyword()
		self.decrypt(chosen_keyword)


if __name__ == "__main__":
	encrypted = "PYIPJMHQYWECJMZQXZZDAGRDTXUZCWPYMSYQHVBWIUICWOBJEFPTNKFLCXKDEYIGSQBIOFPYZXWDTNOAVUVRJUAVXEUMJSGZCEBGYULPVUYJMZDCWDWZUCLWDNZCKFCVCKMHWKFSMYKLFYVBSGZXBMZXJOAZYINABFFWSFCJMZQHKKWFCXUWUNEEJBLRULUMTRWECEDWDYJCWMHUOJWLPZLAAIKHTCVNSZHZWSXNVBNAHEOMZOENVDYZCKUAAKZDYELWEWYVGEMMSYQHVBWPUJCWDHLXYQHLOYQHUFWDGFOYQHVBOALSOFTUSOMZXJOAZFVLWZELOFRNZQVQLNSKEYECUTUWDOUXDOFIICVW"
	v = Vigenere(encrypted=encrypted, language="de")











































