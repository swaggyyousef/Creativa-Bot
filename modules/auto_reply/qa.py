from sentence_transformers import SentenceTransformer, util
import re
import discord
import json
from modules.utils.mysql import execute_query

# Initialize the Sentence Transformer model
model = SentenceTransformer('all-MiniLM-L6-v2')

def get_guild_qa(guild_id: int):
    """
    Retrieves the QA pairs for a guild from the database.
    Expects the `faq` table to have a JSON column 'qa' that is a list of
    dictionaries with keys 'id', 'question', and 'answer'.
    Returns a tuple (common_questions, answers) where:
      - common_questions is a list of questions,
      - answers is a dict mapping each question to its corresponding answer.
    """
    result = execute_query(
        "SELECT qa FROM faq WHERE guild_id = %s",
        (guild_id,),
        fetch_one=True
    )
    faq_list = []
    if result and result[0] and result[0][0]:
        try:
            faq_list = json.loads(result[0][0])
        except (KeyError, json.JSONDecodeError):
            faq_list = []

    common_questions = []
    answers = {}
    for item in faq_list:
        question = item.get("question")
        answer = item.get("answer")
        if question and answer:
            common_questions.append(question)
            # Replace literal '\n' with actual newlines
            formatted_answer = answer.replace('\\n', '\n')
            answers[question] = formatted_answer
    return common_questions, answers

def preprocess_message(text: str) -> str:
    """
    Removes Discord mentions and URLs from the text.
    """
    text = re.sub(r'<@!?[0-9]+>', '', text).strip()
    text = re.sub(r'http\S+', '', text).strip()
    return text

def chunk_message(text: str, chunk_size: int = 10, overlap: int = 8) -> list:
    """
    Splits text into overlapping chunks.
    :param text: The input text.
    :param chunk_size: Maximum number of words per chunk.
    :param overlap: Number of words to overlap between chunks.
    :return: List of text chunks.
    """
    words = text.split()
    if len(words) <= chunk_size:
        return [text]
    chunks = []
    step = chunk_size - overlap
    for i in range(0, len(words), step):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
        if i + chunk_size >= len(words):
            break
    return chunks

def find_best_match(message: discord.Message, threshold: float):
    """
    Computes embeddings for the guild-specific QA pairs and then compares
    overlapping chunks of the user's message against those questions.
    Returns the best matching answer if a similarity score exceeds the threshold.
    """
    # Ensure the message comes from a server (guild)
    if not message.guild:
        return None

    guild_id = message.guild.id
    # Retrieve dynamic QA pairs for this guild
    common_questions, answers = get_guild_qa(guild_id)
    if not common_questions:
        return None

    # Pre-compute embeddings for the common questions
    common_embeddings = model.encode(common_questions)

    content = message.content
    cleaned_message = preprocess_message(content)
    if not cleaned_message or len(cleaned_message.split()) == 1:
        return None

    # Split the cleaned message into overlapping chunks
    chunks = chunk_message(cleaned_message)
    best_overall_score = -1
    best_response = None

    # For each chunk, compute its embedding and calculate cosine similarity
    for chunk in chunks:
        chunk_embedding = model.encode(chunk)
        cosine_scores = util.cos_sim(chunk_embedding, common_embeddings)[0]
        # Look for the best scoring question that exceeds our threshold
        for idx, score in enumerate(cosine_scores):
            if score > threshold and score > best_overall_score:
                best_overall_score = score
                best_response = answers[common_questions[idx]]
    
    # If the best response is callable, call it with the user to get the dynamic result.
    if callable(best_response):
        best_response = best_response(message.author)
    return best_response
