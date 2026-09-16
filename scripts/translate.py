from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

MODEL_NAME = "facebook/nllb-200-distilled-600M"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSeq2SeqLM.from_pretrained(MODEL_NAME)


def translate(text, target_language):
    tokenizer.src_lang = "eng_Latn"

    language_codes = {
        "hindi": "hin_Deva",
        "kannada": "kan_Knda"
    }

    inputs = tokenizer(text, return_tensors="pt")

    outputs = model.generate(
        **inputs,
        forced_bos_token_id=tokenizer.convert_tokens_to_ids(
            language_codes[target_language]
        ),
        max_length=200
    )

    return tokenizer.batch_decode(
        outputs,
        skip_special_tokens=True
    )[0]


if __name__ == "__main__":
    text = "What are my rights if my landlord refuses to return my deposit?"

    print("Hindi:")
    print(translate(text, "hindi"))

    print("\nKannada:")
    print(translate(text, "kannada"))