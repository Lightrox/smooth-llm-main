MODELS = {
    'tinyllama': {
        'model_path': 'TinyLlama/TinyLlama-1.1B-Chat-v1.0',
        'tokenizer_path': 'TinyLlama/TinyLlama-1.1B-Chat-v1.0',
        'conversation_template': 'llama-2'
    },
    'phi2': {
        'model_path': 'microsoft/phi-2',
        'tokenizer_path': 'microsoft/phi-2',
        'conversation_template': 'llama-2'
    },
    'vicuna': {
        'model_path': 'path/to/vicuna/model',
        'tokenizer_path': 'path/to/vicuna/tokenizer',
        'conversation_template': 'vicuna'
    },
    'gemma2b': {
        'model_path': 'google/gemma-2b-it',
        'tokenizer_path': 'google/gemma-2b-it',
        'conversation_template': 'gemma'
    },
    'qwen18b': {
        'model_path': 'Qwen/Qwen-1_8B-Chat',
        'tokenizer_path': 'Qwen/Qwen-1_8B-Chat',
        'conversation_template': 'qwen'
    }
}