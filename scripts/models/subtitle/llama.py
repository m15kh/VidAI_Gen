import os
import ffmpeg
import whisper
import warnings
import tempfile
import yaml
import sys
from typing import List, Tuple
from tqdm import tqdm

sys.path.append(".")
from utils import *

# Uncomment below and comment "from .utils import *", if executing cli.py directly
# import sys
sys.path.append(".")
from auto_subtitle_llama.utils import *

# deal with huggingface tokenizer warning
os.environ["TOKENIZERS_PARALLELISM"] = "false"


def get_audio(paths):
    temp_dir = tempfile.gettempdir()

    audio_paths = {}

    for path in paths:
        print(f"Extracting audio from {filename(path)}...")
        output_path = os.path.join(temp_dir, f"{filename(path)}.wav")

        ffmpeg.input(path).output(
            output_path,
            acodec="pcm_s16le", ac=1, ar="16k"
        ).run(quiet=True, overwrite_output=True)

        audio_paths[path] = output_path

    return audio_paths


def get_subtitles(audio_paths: list, output_srt: bool, output_dir: str, model:whisper.model.Whisper, args: dict, translate_to: str = None) -> Tuple[dict, str]:
    subtitles_path = {}

    for path, audio_path in audio_paths.items():
        srt_path = output_dir if output_srt else tempfile.gettempdir()
        srt_path = os.path.join(srt_path, f"{filename(path)}.srt")
        
        print(
            f"Generating subtitles for {filename(path)}... This might take a while."
        )

        warnings.filterwarnings("ignore")
        print("[Step1] detect language (Whisper)")
        # load audio and pad/trim it to fit 30 seconds
        audio = whisper.load_audio(audio_path)
        audio = whisper.pad_or_trim(audio)
        # make log-Mel spectrogram
        mel = whisper.log_mel_spectrogram(audio, model.dims.n_mels).to(model.device)
        # detect the spoken language
        _, probs = model.detect_language(mel)
        detected_language = max(probs, key=probs.get)
        current_lang = LANG_CODE_MAPPER.get(detected_language, [])
        
        print("[Step2] transcribe (Whisper)")
        if detected_language != "en" and translate_to is not None and translate_to not in current_lang:
            args["task"] = "translate"
            print(f"transcribe-task changed for llama translator")
        
        # Convert language code if present in args
        if "language" in args and args["language"] is not None:
            args["language"] = convert_language_code(args["language"])
            print(f"Using language: {args['language']}")
            
        result = model.transcribe(audio_path, **args)
        
        if translate_to is not None and translate_to not in current_lang:
            print("[Step3] translate (Llama2)")
            text_batch = get_text_batch(segments=result["segments"])
            translated_batch = translates(translate_to=translate_to, text_batch=text_batch)
            result["segments"] = replace_text_batch(segments=result["segments"], translated_batch=translated_batch)
            print(f"translated to {translate_to}")
        
    
        # Save SRT file
        srt_path_base = os.path.splitext(srt_path)[0]

        # if debug:
        #     print(result["segments"])

        print("reforamt_subtitle")
        
        pretty_subtitle = reforamt_subtitle(result["segments"]) #reforamt subtitle to json for currect format moviepy

        with open(f"{srt_path_base}.json", 'w', encoding='utf-8') as json_file:
            json.dump(pretty_subtitle, json_file, indent=4, ensure_ascii=False)
        print(f"json file is saved: {srt_path_base}.json")
        
        
    
            
        # if debug: #TODO add debug for save srt too
        # with open(srt_path, "w", encoding="utf-8") as srt:
        #     write_srt(result["segments"], file=srt)
        # print(f"srt file is saved: {srt_path}")     
                   


    return subtitles_path, detected_language

def translates(translate_to: str, text_batch: List[str], max_batch_size: int = 32):
    model, tokenizer = load_translator()
    
    # split text_batch into max_batch_size
    divided_text_batches = [text_batch[i:i+max_batch_size] for i in range(0, len(text_batch), max_batch_size)]
    
    translated_batch = []
    
    for batch in tqdm(divided_text_batches, desc="batch translate"):
        model_inputs = tokenizer(batch, return_tensors="pt", padding=True)
        generated_tokens = model.generate(
            **model_inputs,
            forced_bos_token_id=tokenizer.lang_code_to_id[translate_to]
        )
        translated_batch.extend(tokenizer.batch_decode(generated_tokens, skip_special_tokens=True))
    
    return translated_batch


