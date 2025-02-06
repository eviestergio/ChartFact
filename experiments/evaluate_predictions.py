## This file will be used to evaluate the scores of the data generated against the gold standard in seed_datasets_100/5_final_dataset_100-new

# Evaluate the labels

#!/usr/bin/env python3
"""
This script evaluates classification metrics given two JSON files.
- fc_entries.json is considered the target (gold standard) entries.
- gpto1mini_entries.json is considered the predicted entries.

Each JSON file is expected to contain a list of entries where each entry is a dictionary
with at least an "image" field and a "label" field.
The script computes the precision (macro), recall (macro), micro F1, and macro F1 scores.
It then saves these scores into 'evaluation_scores.json' in the same folder as the predicted file.
Additionally, the script generates 'unique_label_pairs.json'. For each unique occurrence (based on
the target and predicted labels, compared in a case-insensitive manner), the file includes the 
image (taken from the target entry), the target label, and the predicted label.
"""

import json
import argparse
import os
from sklearn.metrics import precision_score, recall_score, f1_score


def evaluate_scores(target_path, predicted_path):
    # Load the target (gold standard) data
    with open(target_path, "r", encoding="utf-8") as f:
        target_data = json.load(f)
    # Load the predicted data
    with open(predicted_path, "r", encoding="utf-8") as f:
        predicted_data = json.load(f)

    # Assumption: Each file contains a list of dictionaries and each dictionary has 'image' and 'label' fields.
    if len(target_data) != len(predicted_data):
        print(
            f"Warning: Number of entries differ between target ({len(target_data)}) and predicted ({len(predicted_data)}) files."
        )

    # Extract and normalize labels (convert to lowercase for a case-insensitive evaluation)
    true_labels = [entry["label"].lower() for entry in target_data]
    pred_labels = [entry["label"].lower() for entry in predicted_data]

    # Calculate metrics using macro averaging for precision & recall and both micro and macro for F1 scores.
    precision = precision_score(true_labels, pred_labels, average="macro", zero_division=0)
    recall = recall_score(true_labels, pred_labels, average="macro", zero_division=0)
    f1_micro = f1_score(true_labels, pred_labels, average="micro", zero_division=0)
    f1_macro = f1_score(true_labels, pred_labels, average="macro", zero_division=0)

    # Prepare results dictionary for saving
    results = {
        "Precision (Macro)": precision,
        "Recall (Macro)": recall,
        "F1 Score (Micro)": f1_micro,
        "F1 Score (Macro)": f1_macro,
    }

    # Print the evaluation metrics
    print("Evaluation Metrics:")
    print("Precision (Macro): {:.4f}".format(precision))
    print("Recall (Macro):    {:.4f}".format(recall))
    print("F1 Score (Micro):  {:.4f}".format(f1_micro))
    print("F1 Score (Macro):  {:.4f}".format(f1_macro))

    # Determine the folder containing the predicted file and build the output paths
    predicted_dir = os.path.dirname(os.path.abspath(predicted_path))
    eval_output_path = os.path.join(predicted_dir, "evaluation_scores.json")
    unique_pairs_path = os.path.join(predicted_dir, "unique_label_pairs.json")

    # Save the scores to a JSON file in the same folder as gpto1mini_entries.json
    with open(eval_output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=4)
    print(f"Metrics saved to: {eval_output_path}")

    # Create a file containing unique pairs of target and predicted labels.
    # Each entry includes the image key (taken from the target entry),
    # the target label, and the predicted label.
    seen_pairs = set()
    unique_label_pairs = []
    for t_entry, p_entry in zip(target_data, predicted_data):
        t_label = t_entry["label"].lower()
        p_label = p_entry["label"].lower()
        image_value = t_entry.get("image")
        pair = (t_label, p_label)
        if pair not in seen_pairs:
            unique_label_pairs.append({
                "image": image_value,
                "target": t_label,
                "predicted": p_label
            })
            seen_pairs.add(pair)

    with open(unique_pairs_path, "w", encoding="utf-8") as f:
        json.dump(unique_label_pairs, f, indent=4)
    print(f"Unique label pairs saved to: {unique_pairs_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Evaluate classification performance using label matching."
    )
    parser.add_argument(
        "--target",
        type=str,
        default="fc_entries.json",
        help="Path to the target JSON file with gold standard labels (default: fc_entries.json)",
    )
    parser.add_argument(
        "--predicted",
        type=str,
        default="gpto1mini_entries.json",
        help="Path to the predicted JSON file (default: gpto1mini_entries.json)",
    )
    args = parser.parse_args()

    evaluate_scores(args.target, args.predicted)


if __name__ == "__main__":
    main()

