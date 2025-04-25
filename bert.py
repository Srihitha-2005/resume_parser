from transformers import BertTokenizer, BertModel
import torch
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Load pre-trained BERT model and tokenizer
tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

# Function to get BERT embeddings
def get_bert_embedding(text):
    inputs = tokenizer(text, return_tensors='pt', truncation=True, padding=True, max_length=512)
    outputs = model(**inputs)
    return outputs.last_hidden_state.mean(dim=1).detach().numpy()

# Function to calculate similarity score
def calculate_similarity(resume_text, job_description_text):
    resume_embedding = get_bert_embedding(resume_text)
    job_embedding = get_bert_embedding(job_description_text)
    return cosine_similarity(resume_embedding, job_embedding)[0][0]

# Example usage
if __name__ == "__main__":
    job_description = "We are looking for a Python developer with experience in Machine Learning and SQL."
    resume_text = "I am a Python developer with 3 years of experience in Machine Learning and SQL."
    similarity_score = calculate_similarity(resume_text, job_description)
    print(f"Similarity Score: {similarity_score}")