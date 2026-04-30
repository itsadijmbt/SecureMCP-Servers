import boto3
from typing import List
import json
from src.core import config
import asyncio
from botocore.exceptions import ClientError
from src.core.logger import logger

class BedrockService:
    def __init__(self, region_name: str = config.AWS_REGION):
        """Initialize the Bedrock service."""
        self.client = boto3.client("bedrock-runtime", region_name=region_name)
        self.embedding_model_id = config.EMBEDDING_MODEL_ID

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts."""
        if not texts:
            return []

        embeddings = []

        for text in texts:
            try:
                response = self.client.invoke_model(
                    modelId=self.embedding_model_id,
                    contentType="application/json",
                    accept="application/json",
                    body=json.dumps({"inputText": text}),
                )

                response_body = json.loads(response["body"].read())
                embedding = response_body.get("embedding")

                if not embedding:
                    logger.error(f"Failed to generate embedding: {response_body}")
                    # Use a zero vector as fallback
                    embedding = [0.0] * config.VECTOR_DIMENSION

                embeddings.append(embedding)

            except Exception as e:
                logger.error(f"Error generating embeddings: {str(e)}")
                # Use a zero vector as fallback
                embeddings.append([0.0] * config.VECTOR_DIMENSION)

        return embeddings

    async def send_to_bedrock(self, prompt) -> str:
        """Send a prompt to the Bedrock Claude model asynchronously."""
        payload = [{"role": "user", "content": [{"text": prompt}]}]
        model_id = config.LLM_MODEL_ID
        try:
            # Use asyncio.to_thread to call the blocking boto3 client method
            response = await asyncio.to_thread(
                self.client.converse,
                modelId=model_id,
                messages=payload,
            )
            model_response = response["output"]["message"]
            # Concatenate text parts from the model response
            response_text = " ".join(i["text"] for i in model_response["content"])
            return response_text
        except ClientError as err:
            logger.error(f"A client error occurred: {err.response['Error']['Message']}")
            raise

def get_bedrock_service() -> BedrockService:
    """Get a cached Bedrock service instance."""
    return BedrockService()
