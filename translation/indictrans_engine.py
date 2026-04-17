import time
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
import torch

class IndicTransEngine:
    def __init__(self):
        """
        Initializes the IndicTrans2 AI for translating English strictly to multiple Indian languages.
        We are using the '200M' (200 Million parameter) distilled version to ensure it does not 
        exceed the 8GB RAM constraints of your local laptop.
        """
        print("[TRANSLATION INIT] Loading ai4bharat/indictrans2-en-indic-dist-200M...")
        
        # We strictly use the Distilled 200M model to guarantee survival on 8GB laptops
        model_name = "ai4bharat/indictrans2-en-indic-dist-200M"
        
        start_time = time.time()
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
            
            # Load in pure Float32. Do NOT use quantization on this laptop anymore.
            self.model = AutoModelForSeq2SeqLM.from_pretrained(model_name, trust_remote_code=True)
            self.model.eval() # Set hardware to inference mode
            
            print("[TRANSLATION INIT] Hardware target: CPU (Path B Safe Mode).")
            print(f"[TRANSLATION INIT] IndicTrans2 loaded successfully in {time.time() - start_time:.2f} seconds!")
        except Exception as e:
            print(f"[TRANSLATION ERROR] Failed to load model: {e}")
            raise e

    def translate(self, text: str, target_lang="hin_Deva", source_lang="eng_Latn") -> str:
        """
        Takes raw English text and translates it into the target Indian language natively.
        target_lang codes usually follow the IndicNLP BCP-47 format (e.g., 'hin_Deva' for Hindi, 'tam_Taml' for Tamil).
        """
        if not text.strip():
            return ""

        try:
            # AI4Bharat Tokenizer explicitly requires the raw text string to start with the language tag.
            # AND the target language tag right next to it, separated by spaces.
            tagged_text = f"{source_lang} {target_lang} {text}"
            
            inputs = self.tokenizer(
                tagged_text,
                return_tensors="pt"
            )
            
            # Run the AI generation
            # We use forced_bos_token_id to tell the AI which language to output.
            forced_bos_token_id = self.tokenizer.convert_tokens_to_ids(target_lang)
            
            with torch.no_grad(): # Use no_grad to disable training logic and save RAM
                generated_tokens = self.model.generate(
                    **inputs,
                    use_cache=True,
                    min_length=0,
                    max_length=256,
                    num_beams=1, # Lowest beam search to guarantee absolute maximum speed
                    forced_bos_token_id=forced_bos_token_id
                )

                
            # Decode the generated AI tokens back into readable human strings
            with self.tokenizer.as_target_tokenizer():
                translation = self.tokenizer.batch_decode(generated_tokens, skip_special_tokens=True, clean_up_tokenization_spaces=True)[0]
                
            return translation.strip()
            
        except Exception as e:
            print(f"[TRANSLATION INFERENCE ERROR] {e}")
            return ""

    def translate_stream(self, text: str, target_lang="hin_Deva", source_lang="eng_Latn"):
        """
        A Python Generator that yields chunks of translated text natively in real-time.
        Requires TextIteratorStreamer and threading to decouple generation from output.
        """
        if not text.strip():
            return
            
        from transformers import TextIteratorStreamer
        from threading import Thread
        
        tagged_text = f"{source_lang} {target_lang} {text}"
        inputs = self.tokenizer(tagged_text, return_tensors="pt")
        forced_bos_token_id = self.tokenizer.convert_tokens_to_ids(target_lang)
        
        streamer = TextIteratorStreamer(self.tokenizer, skip_prompt=True, skip_special_tokens=True)
        
        generation_kwargs = dict(
            **inputs,
            streamer=streamer,
            max_new_tokens=256,
            num_beams=1,
            forced_bos_token_id=forced_bos_token_id
        )
        
        thread = Thread(target=self.model.generate, kwargs=generation_kwargs)
        thread.start()
        
        for new_text in streamer:
            clean_text = new_text.replace("▁", "")
            if clean_text:
                yield clean_text

