from mcp.server.fastmcp import FastMCP
from mcp.server.fastmcp.prompts import base

mcp = FastMCP("DocumentMCP", log_level="ERROR")

from pydantic import Field, BaseModel

docs = {
    "deposition.md": "This deposition covers the testimony of Angela Smith, P.E.",
    "report.pdf": "The report details the state of a 20m condenser tower.",
    "financials.docx": "These financials outline the project's budget and expenditures.",
    "outlook.pdf": "This document presents the projected future performance of the system.",
    "plan.md": "The plan outlines the steps for the project's implementation.",
    "spec.txt": "These specifications define the technical requirements for the equipment.",
}

# TODO: Write a tool to read a doc
@mcp.tool(
    name = "read_doc_contents",
    description = "Reads the contents of a document given its ID.",
)

def read_doc_contents(
    doc_id: str = Field(..., description="The ID of the document to read.")
):
    if doc_id not in docs:
        return ValueError(f"Document with ID '{doc_id}' not found.")
    return docs[doc_id]

# TODO: Write a tool to edit a doc

@mcp.tool(
    name = "edit_doc_contents",
    description = "Edits the contents of a document given its ID and new content.",
)
def edit_document(
    doc_id: str = Field(..., description="The ID of the document to edit."),
    old_content: str = Field(..., description="The old content of the document."),
    new_content: str = Field(..., description="The new content for the document."),
):
    if doc_id not in docs:
        return ValueError(f"Document with ID '{doc_id}' not found.")
    docs[doc_id] = docs[doc_id].replace(old_content, new_content)
    return f"Document '{doc_id}' updated successfully."


# TODO: Write a resource to return all doc id's

@mcp.resource(
    "docs://documents",
    mime_type="application/json",
    description="Returns a list of all document IDs available in the system.",
)

def list_docs() -> list[str]:
    return list(docs.keys())

# TODO: Write a resource to return the contents of a particular doc
@mcp.resource(
    "docs://document/{doc_id}",
    mime_type="text/plain",
    description="Returns the contents of a specific document given its ID.",
)
def get_doc_contents(doc_id:str) -> str:
    if doc_id not in docs:
        return ValueError(f"Document with ID '{doc_id}' not found.")
    return docs[doc_id]

# TODO: Write a prompt to rewrite a doc in markdown format
@mcp.prompt(
    name="format",
    description="Rewrites a document in markdown format.",
)
def format_doc(
    doc_id: str = Field(description="The ID of the document to format."),
) -> list[base.Message]:
    prompt = f""""
    your goal is to reformat the document to be written with maskdoen syntax. 
    the id of the document is <document_id> {doc_id} </document_id>
    add in headers,bullet points, tables, etc as neccessary. feel free to add in any additional information that you think is relevant to the document.
    use the 'edit_document' tool to make any edits to the document.
    """
    return [base.UserMessage(content=prompt)]
    
# TODO: Write a prompt to summarize a doc


if __name__ == "__main__":
    mcp.run(transport="stdio")
