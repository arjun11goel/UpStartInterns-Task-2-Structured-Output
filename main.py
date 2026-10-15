import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_classic.output_parsers import RetryOutputParser
from langchain_core.runnables import RunnableParallel, RunnablePassthrough

# Load environment variables
load_dotenv()

# 1. Define the Schema (Validation that rejects bad output)
class DeveloperProfile(BaseModel):
    name: str = Field(description="The full name of the developer")
    years_of_experience: int = Field(description="Years of experience as an integer")
    primary_skills: List[str] = Field(description="List of core technical skills")
    is_available: bool = Field(description="Boolean indicating if they are available for hire")

# 2. Setup the Parsers
# Standard parser to format instructions and validate the initial response
base_parser = PydanticOutputParser(pydantic_object=DeveloperProfile)

# Initialize the LLM (Using Google's free tier Gemini model)
llm = ChatGoogleGenerativeAI(model="gemini-3.5-flash-lite")

# Retry parser (The retry/repair path when validation fails)
retry_parser = RetryOutputParser.from_llm(parser=base_parser, llm=llm)

# 3. Define the Prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "Extract the developer information from the text.\n{format_instructions}"),
    ("human", "{text}")
])

# 4. Build the Chain
# We use RunnableParallel to pass both the text and format instructions to the prompt
prompt_chain = RunnableParallel(
    text=RunnablePassthrough(),
    format_instructions=lambda _: base_parser.get_format_instructions()
) | prompt

# The main LLM chain
llm_chain = prompt_chain | llm


def extract_and_validate(input_text: str) -> DeveloperProfile:
    """Extract data, validate it, and repair invalid output if needed."""

    prompt_value = prompt_chain.invoke(input_text)
    raw_response = llm.invoke(prompt_value)

    # Convert the model response into a plain text string.
    raw_text = raw_response.text

    try:
        parsed_data = base_parser.parse(raw_text)
        print("✅ Success on first attempt.")
        return parsed_data

    except Exception as e:
        print(f"⚠️ Validation failed: {e}")
        print("🔧 Triggering repair path...")

        repaired_data = retry_parser.parse_with_prompt(
            raw_text,
            prompt_value
        )

        print("✅ Successfully repaired output.")
        return repaired_data


# 5. Execute
if __name__ == "__main__":
    # Test text with ambiguous data types to test validation
    sample_text = """
    Meet Alex Chen. He's been coding for almost ten years now. 
    He is highly skilled in Python, RAG pipelines, and Docker. 
    Right now, he is not looking for new opportunities.
    """
    
    print("Extracting data...\n")
    final_output = extract_and_validate(sample_text)
    
    print("\n--- Final Validated JSON ---")
    print(final_output.model_dump_json(indent=2))