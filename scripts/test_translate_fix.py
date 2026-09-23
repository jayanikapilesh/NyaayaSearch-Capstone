from rag_core import translate_to_english

test1 = "ಬಂಧನ ವಾರಂಟ್ ಜಾರಿಗೊಳಿಸುವ ವ್ಯಕ್ತಿಗೆ ಸಹಾಯ ಮಾಡಬೇಕೇ"
print("Test 1 (was truncated):")
print(f"  Result: {translate_to_english(test1)}")
print()

test2 = "ಕ್ರಮ ತೆಗೆದುಕೊಳ್ಳುವ ಮೊದಲು ಮ್ಯಾಜಿಸ್ಟ್ರೇಟ್ ದೂರಿನ ಸತ್ಯಾಸತ್ಯತೆ ಪರಿಶೀಲಿಸುತ್ತಾರೆಯೇ"
print("Test 2 (was empty):")
print(f"  Result: {translate_to_english(test2)}")
print()

test3 = "ಜೀವನಾಂಶ ಆದೇಶವನ್ನು ವಾಸ್ತವವಾಗಿ ಹೇಗೆ ಜಾರಿಗೊಳಿಸಲಾಗುತ್ತದೆ"
print("Test 3 (was mistranslated as 'life sentence'):")
print(f"  Result: {translate_to_english(test3)}")
