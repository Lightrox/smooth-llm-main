import torch
from fastchat.model import get_conversation_template
from transformers import AutoTokenizer, AutoModelForCausalLM

class LLM:

    """Forward pass through a LLM."""

    def __init__(
        self, 
        model_path, 
        tokenizer_path, 
        conv_template_name,
        device
    ):

        # Language model
        print(f"Loading model from {model_path}...")
        if device == 'cpu':
            # Use float32 for CPU to avoid compatibility issues
            self.model = AutoModelForCausalLM.from_pretrained(
                model_path,
                torch_dtype=torch.float32,
                trust_remote_code=True,
                low_cpu_mem_usage=True,
                use_cache=True
            )
        else:
            # Use float16 for GPU
            self.model = AutoModelForCausalLM.from_pretrained(
                model_path,
                dtype=torch.float16,
                trust_remote_code=True,
                low_cpu_mem_usage=True,
                use_cache=True,
                device_map="auto"
            )
        
        self.model = self.model.to(device).eval()
        self.tokenizer = AutoTokenizer.from_pretrained(
            tokenizer_path,
            trust_remote_code=True,
            use_fast=False
        )
        self.tokenizer.padding_side = 'left'

        # Pad token fix (add after line 39)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        print(f"Model loaded successfully on {device}")

        # Tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(
            tokenizer_path,
            trust_remote_code=True,
            use_fast=False
        )
        self.tokenizer.padding_side = 'left'
        
        # Set pad token for TinyLlama and other models
        if 'llama' in tokenizer_path.lower() or 'tinyllama' in tokenizer_path.lower():
            self.tokenizer.pad_token = self.tokenizer.unk_token
        elif not self.tokenizer.pad_token:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        # Fastchat conversation template
        try:
            self.conv_template = get_conversation_template(
                conv_template_name
            )
        except Exception as e:
            print(f"Warning: Could not load conversation template '{conv_template_name}': {e}")
            print("Falling back to 'llama-2' template...")
            self.conv_template = get_conversation_template('llama-2')
            
        if self.conv_template.name == 'llama-2':
            self.conv_template.sep2 = self.conv_template.sep2.strip()

    def __call__(self, batch, max_new_tokens=100):

        # Pass current batch through the tokenizer
        batch_inputs = self.tokenizer(
            batch, 
            padding=True, 
            truncation=False, 
            return_tensors='pt'
        )
        batch_input_ids = batch_inputs['input_ids'].to(self.model.device)
        batch_attention_mask = batch_inputs['attention_mask'].to(self.model.device)

        # Forward pass through the LLM
        try:
            with torch.no_grad():
                outputs = self.model.generate(
                    batch_input_ids, 
                    attention_mask=batch_attention_mask, 
                    max_new_tokens=max_new_tokens,
                    do_sample=True,
                    temperature=0.7,
                    top_p=0.9,
                    pad_token_id=self.tokenizer.pad_token_id
                )
        except RuntimeError as e:
            print(f"Error during generation: {e}")
            return []

        # Decode the outputs produced by the LLM
        batch_outputs = self.tokenizer.batch_decode(
            outputs, 
            skip_special_tokens=True
        )
        gen_start_idx = [
            len(self.tokenizer.decode(batch_input_ids[i], skip_special_tokens=True)) 
            for i in range(len(batch_input_ids))
        ]
        batch_outputs = [
            output[gen_start_idx[i]:] for i, output in enumerate(batch_outputs)
        ]

        return batch_outputs