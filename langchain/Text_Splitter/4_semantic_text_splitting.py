# ==============================================================
# SEMANTIC MEANING-BASED TEXT SPLITTING
# ==============================================================
#
# Instead of splitting by character count or document structure,
# this approach splits based on MEANING. It uses embeddings to
# detect where the topic changes in the text, and cuts there.
#
# How it works:
#   1. Splits text into sentences.
#   2. Embeds each sentence into a vector.
#   3. Compares neighbouring sentences by similarity.
#   4. When similarity drops (topic shift), it makes a split.
#
# Best for: long documents where topics change naturally
#           and you want each chunk to be about ONE topic.
#
# ==============================================================

from langchain_huggingface import HuggingFaceEmbeddings

text = """Python is a popular programming language created by Guido van Rossum.
It is known for its simple and readable syntax.
Python supports multiple programming paradigms.

Machine learning is a branch of artificial intelligence.
It allows computers to learn from data without being explicitly programmed.
TensorFlow and PyTorch are popular ML frameworks.

The solar system has eight planets orbiting the Sun.
Earth is the third planet and the only one known to support life.
Mars is often called the Red Planet due to its appearance."""

# Create embeddings model
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Since SemanticChunker requires langchain_experimental, we show
# a practical approach: embed sentences and group by similarity.

# Step 1: Split into sentences
sentences = [s.strip() for s in text.split("\n") if s.strip()]

print("=== All Sentences ===")
for i, s in enumerate(sentences):
    print(f"  {i + 1}. {s}")
print()

# Step 2: Embed each sentence
vectors = embeddings.embed_documents(sentences)

# Step 3: Compare consecutive sentence similarity
from numpy import dot
from numpy.linalg import norm


def cosine_similarity(a, b):
    return dot(a, b) / (norm(a) * norm(b))


print("=== Similarity Between Consecutive Sentences ===")
similarities = []
for i in range(len(vectors) - 1):
    sim = cosine_similarity(vectors[i], vectors[i + 1])
    similarities.append(sim)
    print(f"  Sentence {i + 1} <-> {i + 2}: {sim:.4f}")
print()

# Step 4: Split where similarity drops below threshold
threshold = 0.2
chunks = []
current_chunk = [sentences[0]]

for i, sim in enumerate(similarities):
    if sim < threshold:
        chunks.append("\n".join(current_chunk))
        current_chunk = [sentences[i + 1]]
    else:
        current_chunk.append(sentences[i + 1])
chunks.append("\n".join(current_chunk))

print("=== Semantic Chunks ===")
for i, chunk in enumerate(chunks):
    print(f"--- Chunk {i + 1} ---")
    print(chunk)
    print()
