import streamlit as st
import ollama
import io # 用于处理文件内容
import base64
import PyPDF2 
# 新增导入知识库模块
from knowledge_base import add_to_knowledge_base, search_knowledge_base, OllamaEmbeddings
import os
from langchain_chroma import Chroma
from langchain.text_splitter import CharacterTextSplitter

# 初始化 embedding 模型
embeddings = OllamaEmbeddings(model="bge-m3:latest")

# 知识库存储路径
VECTOR_DB_PATH = "chroma_knowledge_base"

def build_knowledge_base(texts, metadatas=None):
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = text_splitter.create_documents(texts, metadatas=metadatas)
    db = Chroma.from_documents(docs, embeddings, persist_directory=VECTOR_DB_PATH)
    # db.persist() # Chroma 0.4.x 后自动持久化，无需手动调用

def load_knowledge_base():
    if not os.path.exists(VECTOR_DB_PATH):
        return None
    return Chroma(persist_directory=VECTOR_DB_PATH, embedding_function=embeddings)

def add_to_knowledge_base(texts, metadatas=None):
    db = load_knowledge_base()
    text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    if metadatas is not None:
        docs = text_splitter.create_documents(texts, metadatas=metadatas * len(texts) if len(metadatas) == 1 else metadatas)
    else:
        docs = text_splitter.create_documents(texts)
    if db is None:
        build_knowledge_base(texts, metadatas)
    else:
        db.add_documents(docs)
        # db.persist() # Chroma 0.4.x 后自动持久化，无需手动调用

def search_knowledge_base(query, top_k=3):
    db = load_knowledge_base()
    if db is None:
        return []
    docs_and_scores = db.similarity_search_with_score(query, k=top_k)
    return [doc.page_content for doc, score in docs_and_scores]

def delete_by_filename(filename):
    db = load_knowledge_base()
    if db is None:
        return
    db.delete(where={"filename": filename})
    # db.persist() # Chroma 0.4.x 后自动持久化，无需手动调用

def list_all_filenames():
    db = load_knowledge_base()
    if db is None:
        return []
    all_docs = db.get()
    filenames = set()
    for meta in all_docs['metadatas']:
        if meta and 'filename' in meta:
            filenames.add(meta['filename'])
    return list(filenames)

# 明确指定连接到本地的 Ollama 服务
client = ollama.Client(host='http://localhost:11434') 

st.set_page_config(page_title="广腾AI助手", layout="wide")

st.title("广腾AI助手 🤖")

# 初始化聊天历史
if "messages" not in st.session_state:
    st.session_state.messages = []

temp_file_content = None # 在顶层初始化

# 侧边栏用于文件上传和知识库管理
with st.sidebar:
    st.header("文件与知识库管理")

    st.subheader("📚 上传知识库文件")
    kb_file = st.file_uploader("上传知识库文件（内容将永久存入知识库）", key="kb_upload", type=['txt', 'pdf'])
    if kb_file is not None:
        content = kb_file.read().decode("utf-8")
        add_to_knowledge_base([content], metadatas=[{"filename": kb_file.name}])
        st.success(f"文件 '{kb_file.name}' 已添加到知识库！")

    st.subheader("📝 上传临时文件")
    temp_file = st.file_uploader("上传临时文件（仅本次对话可用，不入知识库）", key="temp_upload", type=['txt', 'pdf'])
    if temp_file is not None:
        temp_file_content = temp_file.read().decode("utf-8")
        st.success(f"文件 '{temp_file.name}' 已上传，仅本次对话可用。")

    st.divider()

    with st.expander("🗑️ 知识库管理", expanded=True):
        st.markdown("#### 删除知识文件")
        all_filenames = list_all_filenames()
        selected_file = st.selectbox("选择要删除的知识文件", all_filenames)
        if st.button("删除选中文件的所有知识内容"):
            from knowledge_base import delete_by_filename
            delete_by_filename(selected_file)
            st.success(f"已删除文件 '{selected_file}' 相关的所有知识内容！")
        st.markdown("---")
        st.markdown("#### 当前知识库文件列表")
        st.write(all_filenames if all_filenames else "暂无文件")

# 聊天区（主内容区域）
with st.container():
    st.subheader("💬 聊天区")
    for message in st.session_state.get("messages", []):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("输入你的消息..."):
        # 将用户消息添加到聊天历史
        st.session_state.messages.append({"role": "user", "content": prompt})
        # 在聊天界面显示用户消息
        with st.chat_message("user"):
            st.markdown(prompt)

        # 检索知识库
        kb_contexts = search_knowledge_base(prompt, top_k=3)
        context_text = "\n".join(kb_contexts) if kb_contexts else ""
        # 拼接临时文件内容
        if temp_file_content:
            context_text += f"\n【临时文件内容】\n{temp_file_content}"
        # 构建最终 prompt
        current_message_content = f"请参考以下内容：\n{context_text}\n\n用户的问题/指令是：{prompt}"
        st.info("已从知识库检索相关内容并添加到提示。")

        # 构建发送给 Ollama 的消息
        messages_payload = [
            {'role': m['role'], 'content': m['content']}
            for m in st.session_state.messages[:-1]
        ] # 发送除了当前用户消息之外的所有历史消息

        # 构建发送给 Ollama 的 messages 列表
        message_to_send = {'role': 'user', 'content': current_message_content}

        messages_payload.append(message_to_send)

        # 调用 Ollama 模型生成响应
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            try:
                # 使用 client 对象调用 chat 方法
                stream = client.chat(
                    model='qwen2.5vl:32b', # Ollama 模型名称
                    messages=messages_payload,
                    stream=True,
                )
                for chunk in stream:
                    if chunk['message']['content'] is not None:
                        full_response += chunk['message']['content']
                        message_placeholder.markdown(full_response + "▌") # 显示流式响应

                message_placeholder.markdown(full_response) # 显示最终响应 

            except Exception as e:
                 st.error(f"调用 Ollama 模型时发生错误: {e}")
                 full_response = "无法获取响应。"

            # 将助手的响应添加到聊天历史
            st.session_state.messages.append({"role": "assistant", "content": full_response})

st.caption("© 2024 广腾AI助手 | Powered by Streamlit & Ollama")

