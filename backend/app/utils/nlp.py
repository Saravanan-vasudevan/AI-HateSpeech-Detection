import emoji

import re

import langdetect

import iso639

import nltk
import os

project_root = os.path.dirname(os.path.abspath(__file__))
nltk_data_dir = os.path.join(project_root, 'nltk_data')

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
  if not isinstance(text, str):
    return ""

  text = re.sub(r'https?://\S+|www\.\S+', '[URL]', text)

  text = re.sub(r'@\w+', '[USER]', text)
  text = re.sub(r'#(\w+)', r'\1', text)

  text = emoji.demojize(text).replace(':', ' ')

  obfuscation_dict = {
        '0': 'o', '1': 'i', '3': 'e', '4': 'a', '5': 's',
        '6': 'g', '7': 't', '8': 'b', '@': 'a', '$': 's'
  }
  for char, replacement in obfuscation_dict.items():

    text = re.sub(r'(?<=[a-zA-Z])' + re.escape(char) + r'(?=[a-zA-Z])', replacement, text)

  text = re.sub(r'(.)\1{3,}', r'\1\1\1', text)

  text = re.sub(r'\s+', ' ', text).strip()

  return text

def detect_language(text : str) -> str:
    processed_text = text.strip()

    MIN_TEXT_LENGTH_FOR_DETECTION = 10

    if len(processed_text) < MIN_TEXT_LENGTH_FOR_DETECTION:

        return 'Unknown'

    try:

        detections = langdetect.detect_langs(text = processed_text)

        if detections:

            best_detection = sorted(detections, key=lambda x: x.prob, reverse=True)[0]
            code = best_detection.lang

        else:

            code = 'und'

    except langdetect.lang_detect_exception.LangDetectException as e:
        code = 'und'

    except Exception as e:
        code = 'und'

    try:

        lang = iso639.Language.from_part1(code).name

    except KeyError:
        lang = 'Unknown'

    except Exception as e:
        lang = 'Unknown'

    return lang

def preprocess_for_basic_nlp(text : str) -> str:
   text = preprocess_for_hate_speech(text = text)

   text = text.lower()

   words = nltk.tokenize.word_tokenize(text)

   stop_english = set(nltk.corpus.stopwords.words('english'))

   words = [word for word in words if word not in stop_english]

   stemmer = nltk.stem.PorterStemmer()

   words = [stemmer.stem(word) for word in words]

   sentence = ' '.join(words)
   return sentence
