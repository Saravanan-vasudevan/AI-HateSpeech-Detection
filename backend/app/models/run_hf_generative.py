
from app.models.hf_generative import HuggingFaceGenerative

if __name__ == "__main__":
    print("Initializing Hate Speech Detector...")
    detector = HuggingFaceGenerative()
    print("Hate Speech Detector initialized.")

    text_to_check = "I hate how some people always complain about everything."
    text_to_check_2 = "You are all stupid and should die."

    print(f"\nChecking text: \"{text_to_check}\"")
    preprocessed_text = detector.preprocess(text_to_check)
    probability = detector.predict(preprocessed_text)
    print(f"Hate speech probability: {probability:.4f}")
    contextual_info = detector.predict_text(preprocessed_text)
    print(contextual_info)

    print(f"\nChecking text: \"{text_to_check_2}\"")
    preprocessed_text_2 = detector.preprocess(text_to_check_2)
    probability_2 = detector.predict(preprocessed_text_2)
    print(f"Hate speech probability: {probability_2:.4f}")
    contextual_info_2 = detector.predict_text(preprocessed_text_2)
    print(contextual_info_2)