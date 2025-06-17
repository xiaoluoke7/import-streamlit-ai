# 🚀 AI助手

这是一个基于 Streamlit 和 Ollama 构建的智能AI助手，集成了知识库RAG（检索增强生成）和临时文件上传功能，旨在提供高效、个性化的问答体验。

## ✨ 功能特性

-   **智能问答**：与本地部署的 Ollama 模型进行流畅对话。
-   **知识库管理**：
    -   上传 `txt` 或 `pdf` 文件，自动添加到持久化知识库。
    -   基于知识库内容进行检索增强生成（RAG），提升回答的准确性和专业性。
    -   通过下拉选择，删除知识库中指定文件的所有内容。
-   **临时文件对话**：上传 `txt` 或 `pdf` 文件，其内容仅在当前对话中作为上下文，不持久化。
-   **响应式布局**：简洁明了的 Streamlit 界面，文件管理在侧边栏，聊天在主区域。

## 🛠️ 安装与运行

请按照以下步骤在本地运行此AI助手。

### 前提条件

-   **Python 3.9+**：请从 [Python 官方网站](https://www.python.org/downloads/) 下载并安装。
-   **Ollama**：请从 [Ollama 官方网站](https://ollama.com/) 下载并安装 Ollama 服务。确保 Ollama 服务在后台运行。
-   **Git (可选)**：如果选择通过 Git 克隆项目，则需要安装 Git。

### 运行步骤

你可以选择以下两种方式获取项目代码并运行：

#### 方式一：通过 Git 克隆 (推荐)

1.  **克隆仓库**：
    打开命令行工具，选择一个你希望存放项目的目录，然后克隆你的 GitHub 仓库（请替换为你的实际仓库 URL）：
    ```bash
    git clone https://github.com/你的用户名/你的仓库名.git
    cd 你的仓库名  # 进入项目目录
    ```

2.  **创建 `requirements.txt` 文件**：
    在项目根目录中创建名为 `requirements.txt` 的文件，并粘贴以下内容：
    ```
    streamlit
    ollama
    langchain-chroma
    langchain-community
    langchain
    langchain-core
    langchain-text-splitters
    requests
    PyPDF2
    ```

3.  **安装依赖**：
    在命令行中执行此命令，安装所有必要的 Python 库：
    ```bash
    pip install -r requirements.txt -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple
    ```

#### 方式二：通过 ZIP 下载

1.  **下载并解压项目 ZIP 包**：
    -   访问你的 GitHub 仓库页面。
    -   点击绿色的 "Code" 按钮，然后选择 "Download ZIP"。
    -   将下载的 ZIP 文件解压到你希望存放项目的任意文件夹中（例如 `my_ai_assistant`）。

2.  **创建 `requirements.txt` 文件**：
    在解压后的项目根目录中（例如 `my_ai_assistant` 文件夹内）创建名为 `requirements.txt` 的文件，并粘贴以下内容：
    ```
    streamlit
    ollama
    langchain-chroma
    langchain-community
    langchain
    langchain-core
    langchain-text-splitters
    requests
    PyPDF2
    ```

3.  **打开命令行并进入项目目录**：
    -   打开命令行工具（如 PowerShell、CMD 或终端）。
    -   使用 `cd` 命令进入你解压后的项目文件夹：
        ```bash
        cd path/to/your/unzipped/project/folder  # 请替换为你的实际项目路径
        ```

4.  **安装依赖**：
    在命令行中执行此命令，安装所有必要的 Python 库：
    ```bash
    pip install -r requirements.txt -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple
    ```

#### **所有方式的后续步骤：**

5.  **下载 Ollama 模型**：
    你的应用需要 `qwen2.5vl:32b` (用于问答) 和 `bge-m3:latest` (用于嵌入) 这两个 Ollama 模型。请在命令行中拉取它们：
    ```bash
    ollama pull qwen2.5vl:32b
    ollama pull bge-m3:latest
    ```
   （根据自己来选择模型，然后在model上更改）
    (请确保 Ollama 服务已在后台运行，否则模型将无法下载和加载)

7.  **运行 Streamlit 应用**：
    在项目目录的命令行中执行：
    ```bash
    streamlit run app.py
    ```
    程序将自动在你的默认浏览器中打开应用界面（通常是 `http://localhost:8501`）。
（然后可通过内网穿插或端口转发让别人也使用)
---

## 📁 项目结构
