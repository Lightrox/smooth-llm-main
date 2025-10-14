import os
import torch
import numpy as np
import pandas as pd
from tqdm.auto import tqdm
import argparse
import json
import copy
import random
import string

import lib.perturbations as perturbations
import lib.defenses as defenses
import lib.attacks as attacks
from lib.attacks import CustomPromptAttack
import lib.language_models as language_models
import lib.model_configs as model_configs

def main(args):

    # Create output directories
    os.makedirs(args.results_dir, exist_ok=True)
    
    # Instantiate the targeted LLM
    config = model_configs.MODELS[args.target_model]
    device = 'cuda:0' if torch.cuda.is_available() else 'cpu'
    print(f"Using device: {device}")
    target_model = language_models.LLM(
        model_path=config['model_path'],
        tokenizer_path=config['tokenizer_path'],
        conv_template_name=config['conversation_template'],
        device=device
    )

    # Track if user prompt was used
    user_prompt_used = False
    
    # Create attack instance, used to create prompts
    if args.user_prompt:
        # Use custom user prompt
        print(f"Using custom user prompt: {args.user_prompt}")
        attack = CustomPromptAttack(
            user_prompt=args.user_prompt,
            target_model=target_model
        )
        user_prompt_used = True
    else:
        # Check if user wants to input a prompt interactively
        try:
            user_input = input("\nEnter a custom prompt (or press Enter to use default attack): ").strip()
            if user_input:
                print(f"Using interactive user prompt: {user_input}")
                attack = CustomPromptAttack(
                    user_prompt=user_input,
                    target_model=target_model
                )
                user_prompt_used = True
            else:
                # Use existing attack from logfile
                print(f"Using default attack: {args.attack}")
                attack = vars(attacks)[args.attack](
                    logfile=args.attack_logfile,
                    target_model=target_model
                )
        except (EOFError, KeyboardInterrupt):
            # Handle case where input is not available (e.g., in scripts)
            print(f"Using default attack: {args.attack}")
            attack = vars(attacks)[args.attack](
                logfile=args.attack_logfile,
                target_model=target_model
            )

    # Ask user for number of copies after prompt is set
    try:
        num_copies_input = input(f"\nEnter number of copies (current: {args.smoothllm_num_copies}): ").strip()
        if num_copies_input:
            args.smoothllm_num_copies = int(num_copies_input)
            print(f"Using {args.smoothllm_num_copies} copies")
    except (EOFError, KeyboardInterrupt, ValueError):
        print(f"Using default number of copies: {args.smoothllm_num_copies}")
    
    # Update the defense with new number of copies
    defense = defenses.SmoothLLM(
        target_model=target_model,
        pert_type=args.smoothllm_pert_type,
        pert_pct=args.smoothllm_pert_pct,
        num_copies=args.smoothllm_num_copies
    )

    jailbroken_results = []
    for i, prompt in tqdm(enumerate(attack.prompts[:5])):
        # Set the original prompt for context in jailbreak detection
        defense.set_original_prompt(prompt.perturbable_prompt)
        output = defense(prompt)
        jb = defense.is_jailbroken(output)
        jailbroken_results.append(jb)
        print(f"Prompt {i}: {'unsafe' if jb else 'safe'}")

    print(f'Total prompts processed: {len(jailbroken_results)}')
    print(f'Jailbreak success rate: {np.mean(jailbroken_results) * 100:.2f}%')

    # Save results to a pandas DataFrame
    summary_df = pd.DataFrame.from_dict({
        'Number of smoothing copies': [args.smoothllm_num_copies],
        'Perturbation type': [args.smoothllm_pert_type],
        'Perturbation percentage': [args.smoothllm_pert_pct],
        'JB percentage': [np.mean(jailbroken_results) * 100],
        'Trial index': [args.trial],
        'User prompt used': [user_prompt_used]
    })
    summary_df.to_pickle(os.path.join(
        args.results_dir, 'summary.pd'
    ))
    print(summary_df)


if __name__ == '__main__':
    torch.cuda.empty_cache()

    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--results_dir',
        type=str,
        default='./results'
    )
    parser.add_argument(
        '--trial',
        type=int,
        default=0
    )

    # Targeted LLM
    parser.add_argument(
        '--target_model',
        type=str,
        default='tinyllama',
        choices=['tinyllama', 'phi2', 'gemma2b', 'qwen18b']
    )

    # Attacking LLM
    parser.add_argument(
        '--attack',
        type=str,
        default='GCG',
        choices=['GCG', 'PAIR']
    )
    parser.add_argument(
        '--attack_logfile',
        type=str,
        default='data/GCG/vicuna_behaviors.json'
    )

    # SmoothLLM
    parser.add_argument(
        '--smoothllm_num_copies',
        type=int,
        default=10,
    )
    parser.add_argument(
        '--smoothllm_pert_pct',
        type=int,
        default=10
    )
    parser.add_argument(
        '--smoothllm_pert_type',
        type=str,
        default='RandomPatchPerturbation',
        choices=[
            'RandomSwapPerturbation',
            'RandomPatchPerturbation',
            'RandomInsertPerturbation'
        ]
    )

    # User input prompt option
    parser.add_argument(
        '--user_prompt',
        type=str,
        default=None,
        help='Custom user prompt to test instead of using attack logfile'
    )

    args = parser.parse_args()
    main(args)