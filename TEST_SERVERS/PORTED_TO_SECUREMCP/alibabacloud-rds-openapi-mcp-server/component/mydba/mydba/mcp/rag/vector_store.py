# -*- coding: utf-8 -*-
import os
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from pydantic import BaseModel, Field
from typing import Any, List, Dict

current_dir = os.path.dirname(os.path.abspath(__file__))

class VectorStore(BaseModel):
    embedding: Any = Field(None, description="文本向量化模型")
    dir_path: str = Field("", description="向量库保存路径")
    vectorstores: Dict[str, Any] = Field({}, description="向量库集合")

    def __init__(self, model_name: str, api_key: str, base_url: str, dir_path: str):
        """
        embedding 模型初始化，若传入了 openai 的 api_key，则使用 openai 的 Embeddings 模型
        若传入了其他模型的 api_key，则使用兼容的 Embeddings 模型
        否则使用本地 Embeddings 模型
        Args:
            model_name (str): embedding 模型名称。
            api_key (str): API key。
            base_url (str): API base URL。
            dir_path (str): 向量库保存路径。
        """
        super().__init__()
        if "openai" in base_url and api_key:
            from langchain.embeddings import OpenAIEmbeddings
            if not model_name:
                model_name = "text-embedding-ada-002"
            embedding = OpenAIEmbeddings(model=model_name, openai_api_key=api_key)
        elif api_key and base_url:
            from embeddings import CompatibleEmbeddings
            if not model_name:
                model_name = "text-embedding-v2"
            embedding = CompatibleEmbeddings(model=model_name, openai_api_key=api_key, base_url=base_url, chunk_size=10)
        else:
            # 使用本地 Embeddings 模型，从 https://www.modelscope.cn/ 上下载
            from langchain_huggingface import HuggingFaceEmbeddings
            from modelscope.hub.snapshot_download import snapshot_download
            if not model_name:
                model_name = 'maidalun/bce-embedding-base_v1'
            model_dir = os.path.join(current_dir, model_name)
            snapshot_download(model_name, local_dir=model_dir)
            embedding = HuggingFaceEmbeddings(model_name=model_dir)
        self.embedding = embedding
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        self.dir_path = dir_path
        self.vectorstores = {}
                
    def load_vectorstore_by_name(self, vectorstore_name: str) -> FAISS:
        """
        根据 vectorstore_name 返回对应的向量库对象
        """
        if vectorstore_name in self.vectorstores:
            return self.vectorstores[vectorstore_name]
        vectorstore_dir = os.path.join(self.dir_path, vectorstore_name)
        if os.path.isdir(vectorstore_dir) and os.path.exists(os.path.join(vectorstore_dir, 'index.faiss')):
            vectorstore = FAISS.load_local(vectorstore_dir, embeddings=self.embedding, allow_dangerous_deserialization=True)
            self.vectorstores[vectorstore_name] = vectorstore
            return vectorstore
        return None

    def create_vectorstore_by_file(self, file: str, vectorstore_name: str) -> None:
        """
        根据传入的文件名，创建向量库
        Args:
            file (str): 文件名。
            vectorstore_name (str): 向量库保存路径。
        Returns:
            vectorstore (FAISS): 向量库。
        """
        data = self._load_document(file)
        chunks = self._chunk_data(data)
        vectorstore = FAISS.from_documents(chunks, embedding=self.embedding)
        vectorstore_dir = os.path.join(self.dir_path, vectorstore_name)
        vectorstore.save_local(vectorstore_dir)
    
    def _load_document(self, file: str) -> List[Document]:
        """
        读取文件
        Args:
            file (str): 文件名。
        Returns:
            data (List[Document]): 文档数据。
        """
        name, extension = os.path.splitext(file)

        if extension == '.pdf':
            from langchain_community.document_loaders import PyPDFLoader
            print(f'Loading {file}')
            loader = PyPDFLoader(file)
        elif extension == '.docx':
            from langchain_community.document_loaders import Docx2txtLoader
            print(f'Loading {file}')
            loader = Docx2txtLoader(file)
        elif extension == '.txt' or extension == '.md':
            from langchain_community.document_loaders import TextLoader
            loader = TextLoader(file)
        else:
            print('Document format is not supported!')
            return None 

        data = loader.load()
        return data

    def _chunk_data(self, data: List[Document], chunk_size : int=20, chunk_overlap: int=0) -> List[Document]:
        """
        对数据进行切分，以 ; 进行分割
        Args:
            data (List[Document]): 文档数据。
            chunk_size (int): 切分大小，设置成一个较小的数，可以将完整语句切分出来。
            chunk_overlap (int): 切分重叠。
        Returns
            chunks (List[Document]): 切分后的数据。
        """
        from langchain.text_splitter import RecursiveCharacterTextSplitter
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap, separators=[";\n"], keep_separator=False)
        chunks = text_splitter.split_documents(data)
        return chunks
