# Set up the query for generating responses
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential
from azure.core.exceptions import HttpResponseError, ClientAuthenticationError
from openai import AzureOpenAI
import sys



from dotenv import load_dotenv
load_dotenv()


# Set endpoints and deployment model (provide the name of the deployment)
AZURE_SEARCH_ENDPOINT = ""
AZURE_OPENAI_ENDPOINT = ""
AZURE_DEPLOYMENT_MODEL = "dev-gpt-4.1-mini"
AZURE_SEARCH_API_KEY = ""
AZURE_OPENAI_API_KEY = ""

# Azure 설정
# AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
# AZURE_OPENAI_KEY = os.getenv("AZURE_OPENAI_KEY")



try:
    search_credential = AzureKeyCredential(AZURE_SEARCH_API_KEY)

    # Initialize the OpenAI client
    openai_client = AzureOpenAI(
        api_version="2024-06-01",
        azure_endpoint=AZURE_OPENAI_ENDPOINT,
        api_key=AZURE_OPENAI_API_KEY
    )

    # Initialize the search client
    search_client = SearchClient(
        endpoint=AZURE_SEARCH_ENDPOINT,
        index_name="hotels-sample-index",
        credential=search_credential
    )

except ClientAuthenticationError as auth_error:
    print("인증 오류가 발생했습니다. API 키와 엔드포인트를 확인하세요:")
    print(auth_error.message)
    sys.exit(1)

except HttpResponseError as http_error:
    print("HTTP 응답 오류가 발생했습니다:")
    print(http_error.message)
    sys.exit(1)

except exception as e:
    print("알 수 없는 오류가 발생했습니다:")
    print(e.message)
    sys.exit(1)




# This prompt provides instructions to the model
GROUNDED_PROMPT = """
You are a **Tibero Database expert and technical document summarization AI**.
When a Tibero technical document or error log is provided, you must produce the following outputs in English:
1. **Summary** – Include the core structure, main concepts, and key procedures.
2. **Error / Code Analysis** – Describe the cause, corrective actions, and related manual or documentation sections.
3. **Additional Checks Needed (x2)** – Suggest two follow-up points or items that require further verification.
# Query: {query}
# Sources:\n{sources}
"""

# Query is the question being asked. It's sent to the search engine and the LLM.
query = """
TBR-12170: Timeout occurred while waiting for a response from the server.
This error may indicate that the server is not reachable or network latency is high.
Check listener configuration and firewall rules.
"""


print(query)