# Importing emoji library
# - We are using this functionality because emoji's have sematic relevance
#   and therefore, we should try and keep it for detection
import emoji

# Import regular expressions
# - This is needed to allow us to correct for certain techniques
#   like twitter handles and repeated characters
import re

# Importing ability to detect languages
import langdetect

# Importing language classification system
import iso639

# Importing nltk (and os to locate the data)
import nltk
import os

# Define the relative path to your nltk_data folder from this script's location
# If 'main.py' is in 'root/', and 'nltk_data' is also in 'root/', then:
project_root = os.path.dirname(os.path.abspath(__file__))
nltk_data_dir = os.path.join(project_root, 'nltk_data')

# Add this directory to NLTK's search path
if nltk_data_dir not in nltk.data.path:
  nltk.data.path.append(nltk_data_dir)

def preprocess_for_hate_speech(text : str) -> str:
  '''
  Lightweight preprocessing pipeline optimized for hate speech detection.
  This model has been simplified as transformers can handle lots of the
  quirks that can arise is speech

  Parameters:
  - text (str): Input text to preprocess

  Returns:
  - str: Preprocessed text ready for your prediction algorithm
  '''
  # Error case
  # - If for whatever reason a non-text argument is passed to the algorithm, I am
  #   going to return a null string
  if not isinstance(text, str):
    return ""

  # Correction 1
  # - Rather than leave URLs in the text / speech, I am going to replace
  #   them with a standardised URL token
  text = re.sub(r'https?://\S+|www\.\S+', '[URL]', text)

  # Correction 2
  # - As some of the data sources are tweets, they may have users and hashtags
  # - To correct for this, I am going to put a user token instead and remove hash
  #   tags
  text = re.sub(r'@\w+', '[USER]', text)
  text = re.sub(r'#(\w+)', r'\1', text)  # Convert hashtags to words

  # Correction 3
  # - People may put emojis in their text (particularly if it is a tweet)
  # - Rather than removing them all together, I am going to replace emojis with
  #   there description. This is hopefully advantageous as they covey lots of
  #   emotion
  text = emoji.demojize(text).replace(':', ' ')

  # Handle obfuscation techniques that models might struggle with
  # - Sometimes, users may add additional characters to perhaps put
  #   expletives into text without the content being flagged as a swear word
  # - What I am going to is replace these with the likely character the user
  #   was intending to use
  obfuscation_dict = {
        '0': 'o', '1': 'i', '3': 'e', '4': 'a', '5': 's',
        '6': 'g', '7': 't', '8': 'b', '@': 'a', '$': 's'
  }
  for char, replacement in obfuscation_dict.items():

    # ... Only replacing when it is likely to be an obfuscation
    text = re.sub(r'(?<=[a-zA-Z])' + re.escape(char) + r'(?=[a-zA-Z])', replacement, text)

  # Correction 5 - Repeated characters
  # - Sometimes, users may repeat characters for emphassis
  # - I am going to limit them to 3
  text = re.sub(r'(.)\1{3,}', r'\1\1\1', text)  # Limit to 3 repetitions max

  # Correct 6
  # - Remove extra whitespace
  text = re.sub(r'\s+', ' ', text).strip()

  return text

def detect_language(text : str) -> str:
    '''
    Detects the language of the given text using langdetect.
    Includes robust error handling and a more sensible fallback.

    Input args:
    - text (str) : String to be classified

    Return:
    - (str) : Full name of language, or 'Unknown' if detection fails
    '''
    # Preprocess the text slightly to help langdetect, but avoid
    processed_text = text.strip()

    # If the text is too short after stripping whitespace, langdetect might fail.
    MIN_TEXT_LENGTH_FOR_DETECTION = 10 

    # Check - Is our text of suitable length?
    if len(processed_text) < MIN_TEXT_LENGTH_FOR_DETECTION:
        
        # Returning unknown as cannot train
        return 'Unknown' 

    ################################################
    #          Stage 1 - Classification            #
    ################################################
    try:
        
        # Attempt to perform classification
        # langdetect.detect_langs returns a list of Language objects
        detections = langdetect.detect_langs(text = processed_text)
        
        # Check - Was a detection made?
        if detections:
            
            # Sort by probability in descending order and take the top one
            best_detection = sorted(detections, key=lambda x: x.prob, reverse=True)[0]
            code = best_detection.lang
        
        # Else, it couldn't predict, so putting as unknown
        else:
            
            # If detect_langs returns an empty list, it means no language was detected confidently
            code = 'und' # 'und' is the ISO 639-2/T code for 'Undetermined'
    
    # Catch 1 - Unreliable language detection
    except langdetect.lang_detect_exception.LangDetectException as e:
        code = 'und' # Use 'und' for undetermined
    
    # Catch - Other general exceptions
    except Exception as e:
        code = 'und' # Use 'und' for undetermined

    # Determining the full language name from the code
    try:
        
        # iso639.Language.from_part1 will raise a KeyError if the code is not found
        lang = iso639.Language.from_part1(code).name
    
    # Catch 1 - Unknown code (such as und)
    except KeyError:
        # If the code is 'und' or some other unrecognised code by iso639
        lang = 'Unknown'
    
    # Catch 2 - Some other errors in detection
    except Exception as e:
        lang = 'Unknown'

    # Returning the language
    return lang

def preprocess_for_basic_nlp(text : str) -> str:
   '''
   This is an enhanced pre-processing routine
   that is designed specifically for the 
   traditional ML approaches for hate speech
   detection

   Why:
   - Traditional approaches (like TF-IDF) are more
     suspectible to the noise from stop-words and
     casing (in a way that transformers are not so)
    - Therefore, it is necessary to perform additional
      processing to combat this

    Input args:
    - text (str) : Text to process

    Return:
    - (str) Processed string with additional processing
   '''
   # Performing existing processing (which is done on all text)
   text = preprocess_for_hate_speech(text = text)

   text = text.lower()

   words = nltk.tokenize.word_tokenize(text)

   # Establishing the English stop words
   stop_english = set(nltk.corpus.stopwords.words('english'))

   # Filtering out the stop-words
   words = [word for word in words if word not in stop_english]

   stemmer = nltk.stem.PorterStemmer()

   words = [stemmer.stem(word) for word in words]

   # Creating the sentence
   sentence = ' '.join(words)
   return sentence
