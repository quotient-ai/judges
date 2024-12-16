import os
from datasets import Dataset
from huggingface_hub import Repository

# Configuration
file_path = "natural-qa-random-100-with-AI-search-answers.csv"  # Path to your CSV file
repo_name = "quotientai/natural-qa-random-100-with-AI-search-answers"  # Hugging Face dataset repo name
username = "jamesliounis"  # Your Hugging Face username
repo_url = f"https://huggingface.co/datasets/{repo_name}"  # Hugging Face repo URL
output_dir = "natural-qa-random-100-with-AI-search-answers"  # Directory to save the processed dataset

# Step 1: Load the CSV file into a Hugging Face Dataset
print("Loading the CSV file into a Hugging Face Dataset...")
dataset = Dataset.from_csv(file_path)
print(dataset)

# Step 2: Save the dataset in the proper format for Hugging Face
print("Saving the dataset to disk...")
os.makedirs(output_dir, exist_ok=True)
dataset.save_to_disk(output_dir)


# Step 4: Push to the Hugging Face Repository
print("Initializing the Hugging Face repository...")
repo = Repository(local_dir=output_dir, clone_from=repo_url)

print("Adding and committing the dataset...")
repo.git_add()
repo.git_commit("Add Natural QA Random 100 with AI Search Answers dataset")

print("Pushing the dataset to the Hugging Face repository...")
repo.git_push()

print("Dataset pushed successfully!")
