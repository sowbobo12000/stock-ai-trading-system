from sentence_transformers import SentenceTransformer
import pickle

def vectorize_texts(texts):
    model = SentenceTransformer("all-MiniLM-L6-v2")
    vectors = model.encode(texts)
    return vectors

texts = ["주가 변동성과 옵션 거래의 상관관계", "머신러닝을 이용한 금융 예측"]
vectors = vectorize_texts(texts)

# 저장
with open("data/vector_storage/financial_vectors.pkl", "wb") as f:
    pickle.dump(vectors, f)
