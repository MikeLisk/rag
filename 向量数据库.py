import uuid
import chromadb
import requests
def ollama_embedding_by_api(text):
    res = requests.post(
    url="http://127.0.0.1:11434/api/embeddings",
    json={
        "model": "bge-m3",
        "prompt": text
    }
)

    embedding_list = res.json()['embedding']
    return embedding_list

client = chromadb.PersistentClient(path="db/chroma_ demo")  # 数据库 类似=文件夹
collection = client.get_or_create_collection(name="collection_v1")  # 集合 类似=表格

# 构造数据
documents = ["营血虚滞证症状：头晕目眩，心悸失眠，面色无华，或妇人月经不调、量少经闭，脐腹作痛药方：四物汤。", "风寒感冒症状：恶寒重，发热轻，无汗，头身疼痛，鼻塞流清涕，舌苔薄白，脉浮紧药方：麻黄汤。", "风热感冒症状：发热重，恶寒轻，有汗，头胀痛，鼻塞流黄涕，咽喉红肿疼痛，口渴，舌尖红，苔薄黄，脉浮数药方：银翘散。"]
# 如 ["风寒感冒", "感冒治疗", "心悸可用"]
ids = [str(uuid.uuid4()) for _ in documents]
# 如 ["xx", "yy", "bb"]
embeddings = [ollama_embedding_by_api(text) for text in documents]
# 如 [[-0.24,-0.12], [-0.4,-0.2], [0.89,-0.2]]

# 插入数据
collection.add(
    ids=ids,
    documents=documents,
    embeddings=embeddings
)

# 关键词搜索
qs = "感冒喝水"
qs_embedding = ollama_embedding_by_api(qs)
res = collection.query(query_embeddings=[qs_embedding], query_texts=qs, n_results=1)
print(res)