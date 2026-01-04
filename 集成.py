import uuid
import chromadb
import requests

def file_chunk_list():
    # 1.读取文件内容
    with open("中医v1.txt", encoding='utf-8', mode='r') as fp:
        data = fp.read()
    # 2.根据换行分割
    chunk_list = data.split("\n\n")
    return [chunk for chunk in chunk_list if chunk]

def ollama_embedding_by_api(text):
    res = requests.post(
        url="http://127.0.0.1:11434/api/embeddings",
        json={
            "model": "bge-m3",
            "prompt": text
        }
    )
    embedding = res.json()["embedding"]
    return embedding
def ollama_generate_by_api(prompt):
    response = requests.post(
        url="http://127.0.0.1:11434/api/generate",
        json={
            "model": "deepseek-r1:1.5b",
            "prompt": prompt,
            "stream": False,
            "temperature": 0.1
        }
    )
    res = response.json()["response"]
    return res
def initial():
    client = chromadb.PersistentClient(path="db/chroma_demo")
    # 创建集合
    client.delete_collection("collection_v2")
    collection = client.get_or_create_collection(name="collection_v2")
    # 构造数据
    documents = file_chunk_list()
    # print(len(documents))
    ids = [str(uuid.uuid4()) for _ in range(len(documents))]
    embeddings = [ollama_embedding_by_api(text) for text in documents]
    # print(len(embeddings))
    # 插入数据
    collection.add(
        ids=ids,
        documents=documents,
        embeddings=embeddings
    )
    
def run():
    # 调用知识库
    qs = "风寒感冒"
    qs_embedding = ollama_embedding_by_api(qs)
    
    client = chromadb.PersistentClient(path="db/chroma_demo")
    collection = client.get_collection(name="collection_v2")
    # print(collection)
    res = collection.query(query_embeddings=[qs_embedding, ], n_results=2)
    result = res["documents"][0]
    context = "\n".join(result)

    prompt = f"请你做一个问诊的机器人，但是只能根据参考信息回答用户问题，如果参考信息不足以回答用户问题，请回复不知道，不要编造虚假信息，用中文回答。\n参考信息：{context}\n\n来回答问题：{qs}"
    result = ollama_generate_by_api(prompt)
    print(result)


if __name__ == '__main__':
    initial()
    run()