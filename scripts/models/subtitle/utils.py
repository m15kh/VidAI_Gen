import os
from typing import Iterator, TextIO, List
import json




LANG_CODE_MAPPER = {
    "en": ["english", "en_XX"],
    "zh": ["chinese", "zh_CN"],
    "de": ["german", "de_DE"],
    "es": ["spanish", "es_XX"],
    "ru": ["russian", "ru_RU"],
    "ko": ["korean", "ko_KR"],
    "fr": ["french", "fr_XX"],
    "ja": ["japanese", "ja_XX"],
    "pt": ["portuguese", "pt_XX"],
    "tr": ["turkish", "tr_TR"],
    "pl": ["polish", "pl_PL"],
    "nl": ["dutch", "nl_XX"],
    "ar": ["arabic", "ar_AR"],
    "sv": ["swedish", "sv_SE"],
    "it": ["italian", "it_IT"],
    "id": ["indonesian", "id_ID"],
    "hi": ["hindi", "hi_IN"],
    "fi": ["finnish", "fi_FI"],
    "vi": ["vietnamese", "vi_VN"],
    "he": ["hebrew", "he_IL"],
    "uk": ["ukrainian", "uk_UA"],
    "cs": ["czech", "cs_CZ"],
    "ro": ["romanian", "ro_RO"],
    "ta": ["tamil", "ta_IN"],
    "no": ["norwegian", ""],
    "th": ["thai", "th_TH"],
    "ur": ["urdu", "ur_PK"],
    "hr": ["croatian", "hr_HR"],
    "lt": ["lithuanian", "lt_LT"],
    "ml": ["malayalam", "ml_IN"],
    "te": ["telugu", "te_IN"],
    "fa": ["persian", "fa_IR"],
    "lv": ["latvian", "lv_LV"],
    "bn": ["bengali", "bn_IN"],
    "az": ["azerbaijani", "az_AZ"],
    "et": ["estonian", "et_EE"],
    "mk": ["macedonian", "mk_MK"],
    "ne": ["nepali", "ne_NP"],
    "mn": ["mongolian", "mn_MN"],
    "kk": ["kazakh", "kk_KZ"],
    "sw": ["swahili", "sw_KE"],
    "gl": ["galician", "gl_ES"],
    "mr": ["marathi", "mr_IN"],
    "si": ["sinhala", "si_LK"],
    "km": ["khmer", "km_KH"],
    "af": ["afrikaans", "af_ZA"],
    "ka": ["georgian", "ka_GE"],
    "gu": ["gujarati", "gu_IN"],
    "lb": ["luxembourgish", "ps_AF"],
    "tl": ["tagalog", "tl_XX"],
}

def convert_language_code(lang_code):
    """Convert language codes from NLLB format (xx_XX) to Whisper format (xx)."""
    if not lang_code:
        return None
    # If it contains an underscore, take the part before the underscore
    if "_" in lang_code:
        return lang_code.split("_")[0]
    return lang_code


def str2bool(string):
    string = string.lower()
    str2val = {"true": True, "false": False}

    if string in str2val:
        return str2val[string]
    else:
        raise ValueError(
            f"Expected one of {set(str2val.keys())}, got {string}")


def format_timestamp(seconds: float, always_include_hours: bool = False):
    assert seconds >= 0, "non-negative timestamp expected"
    milliseconds = round(seconds * 1000.0)

    hours = milliseconds // 3_600_000
    milliseconds -= hours * 3_600_000

    minutes = milliseconds // 60_000
    milliseconds -= minutes * 60_000

    seconds = milliseconds // 1_000
    milliseconds -= seconds * 1_000

    hours_marker = f"{hours:02d}:" if always_include_hours or hours > 0 else ""
    return f"{hours_marker}{minutes:02d}:{seconds:02d},{milliseconds:03d}"


def write_srt(transcript: Iterator[dict], file: TextIO):
    for i, segment in enumerate(transcript, start=1):
        print(
            f"{i}\n"
            f"{format_timestamp(segment['start'], always_include_hours=True)} --> "
            f"{format_timestamp(segment['end'], always_include_hours=True)}\n"
            f"{segment['text'].strip().replace('-->', '->')}\n",
            file=file,
            flush=True,
        )


def filename(path):
    return os.path.splitext(os.path.basename(path))[0]


def load_translator():
    from transformers import MBartForConditionalGeneration, MBart50TokenizerFast
    model = MBartForConditionalGeneration.from_pretrained("SnypzZz/Llama2-13b-Language-translate")
    tokenizer = MBart50TokenizerFast.from_pretrained("SnypzZz/Llama2-13b-Language-translate", src_lang="en_XX")
    return model, tokenizer

def get_text_batch(segments:List[dict]):

    text_batch = []
    for i, segment in enumerate(segments):
        text_batch.append(segment['text'])
    return text_batch

def replace_text_batch(segments:List[dict], translated_batch:List[str]):
    for i, segment in enumerate(segments):
        segment['text'] = translated_batch[i]
    return segments




def reforamt_subtitle(json_subtitle):
    
    # Characters to filter out
    filter_chars = [';', '"', "'", ',', '.', '!', '?', '،',':', '؟', '؛', '(', ')', '[', ']', '{', '}', '<', '>', '«', '»']
    # Process each entry
    for entry in json_subtitle:
        # Clean the main text field
        text = entry['text']
        for char in filter_chars:
            text = text.replace(char, '')
        entry['text'] = text.strip()


    """
    Process subtitle file to add start and end times for each word based on word length.
    """

    # Process each subtitle entry
    for subtitle in json_subtitle:
        start_time = subtitle['start']
        end_time = subtitle['end']
        total_duration = end_time - start_time
        
        # Ensure 'words' key exists, initialize as an empty list if not present
        if 'words' not in subtitle:
            subtitle['words'] = []
        
        # Extract words from the text
        words = subtitle['text'].split()
        
        # Calculate total length of all words
        total_length = sum(len(word.strip()) for word in words)
        
        # Edge case: if total_length is 0, distribute time equally
        if total_length == 0:
            time_per_word = total_duration / len(words) if words else 0
            current_time = start_time
            
            for word in words:
                word_data = {
                    'word': " " + word,  # Add space at the beginning
                    'start': round(current_time, 3),
                    'end': round(current_time + time_per_word, 3)
                }
                subtitle['words'].append(word_data)
                current_time += time_per_word
        else:
            # Distribute time based on word length
            current_time = start_time
            for word in words:
                word_length = len(word.strip())
                # Calculate word duration based on its proportion of total length
                if word_length == 0:  # Handle empty words
                    word_duration = total_duration / (2 * len(words))  # Give half of average time
                else:
                    word_duration = (word_length / total_length) * total_duration
                
                word_data = {
                    'word': " " + word,  # Add space at the beginning
                    'start': round(current_time, 3),
                    'end': round(current_time + word_duration, 3)
                }
                subtitle['words'].append(word_data)
                current_time += word_duration
            
            # Adjust the last word to exactly match the subtitle end time
            if words:
                subtitle['words'][-1]['end'] = end_time
    
    # Merge words starting with "می" with the next word (if needed)
    """
    Merge words starting with "می" with the next word.
    For example, "می" and "کند" become "میکند".
    """
    for subtitle in json_subtitle:
        words = subtitle['words']
        i = 0
        while i < len(words) - 1:  # Ensure we don't go out of bounds with next word check
            word = words[i]
            # Check if current word is "می" (with or without space)
            if word['word'].strip() == "می":
                next_word = words[i + 1]
                # Create merged word - ensure no space between می and the next word
                merged_word = {
                    "word": " " + word['word'].strip() + next_word['word'].strip(),  # Add space at the beginning of the merged word
                    "start": word['start'],
                    "end": next_word['end']
                }
                # Replace the two words with the merged one
                words[i] = merged_word
                words.pop(i + 1)
            else:
                i += 1
                
    return json_subtitle
     



if __name__ == "__main__":
    
    input_file = "/home/rteam2/m15kh/auto-subtitle/notebook/auto-subtitle-translate/subtitled/time.json"
    with open(input_file, 'r', encoding='utf-8') as file:
        data = json.load(file)
        
    # remove_punctuation(data)
    processed_json_subtitle = reforamt_subtitle(data)
    output_file = os.path.join(os.path.dirname(input_file), "reforamt_subtile_" + os.path.basename(input_file))
    with open(output_file, 'w', encoding='utf-8') as file:
        json.dump(processed_json_subtitle, file, ensure_ascii=False, indent=4)
    print(f"Processing complete. Results saved to {output_file}")


