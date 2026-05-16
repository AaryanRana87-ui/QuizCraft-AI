def chunk_text(text,chunk_size=600):
    #saftey check
    #checking for text , and if there is nothing after
    # removing spaces : then the condition is turns True
    if not text.strip(): # if "Nothing" comes in hand after removing spaces ( empty string is a false condition in python)

        print("Empty text!Check PDF or page range.")
        return[]
    words = text.split() # spliting words 
    return [" ".join(words[i:i+chunk_size]) # words till chunksize = 600
            # " join " here does join words till 600 words and seperator is space
            #hence first 600 words are joined and sepearated by space.
            #then that to next 600 , then next 600, and so on
           for i in range(0,len(words), chunk_size)] 
             
#Alternate for the code inside "return" : 
# chunks = []
#for i in range(0, len(words), chunk_size):
 #   chunk = " ".join(words[i:i+chunk_size])
 #   chunks.append(chunk)

#return chunks

# written between [] so that all this is returned in list,
# with each element being of 600 words
#so in chunking: we created a list jisme har ek element 
#string hai , and each element is string with 600 words each



