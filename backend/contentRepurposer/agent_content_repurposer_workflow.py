from typing import Dict, Any
from pydantic import BaseModel
from .content_repurposer_workflow_model import build_repurposer_graph, RepurposerState

# Pydantic model to validate the input from the frontend
class RepurposerInput(BaseModel):
    article_text: str

class ContentRepurposerAgent:
    """
    A simple wrapper class for the content repurposing LangGraph workflow.
    This class is called by the API router.
    """
    
    def __init__(self):
        """
        Initializes the agent by building and compiling the LangGraph workflow.
        """
        self.graph = build_repurposer_graph()

    def invoke(self, data: RepurposerInput) -> Dict[str, Any]:
        """
        Runs the content repurposing workflow.
        
        Args:
            data: A RepurposerInput object containing the article_text.
            
        Returns:
            A dictionary formatted for the frontend, containing the
            'repurposed_content' package.
        """
        try:
            # 1. Prepare the initial state for the graph
            # The RepurposerState keys must match the graph's state
            initial_state: RepurposerState = {
                "article_text": data.article_text,
                
                # Set default Nones for all output fields
                "summary": None,
                "social_posts": None,
                "faq_section": None,
                "entities": None,
                "final_package": None,
            }

            # 2. Run the graph
            # The graph will run all parallel nodes and then the compile node
            final_state = self.graph.invoke(initial_state)

            # 3. Extract the final package
            # This 'final_package' is assembled by the 'compile_package' node
            # and matches the 'RepurposeResults' interface in React
            result_package = final_state.get("final_package")

            if result_package is None:
                raise Exception("Workflow finished but final_package was not compiled.")

            # 4. Return the response in the format the frontend expects
            # The frontend (ContentRepurposerPage.tsx) expects: { repurposed_content: ... }
            return {"repurposed_content": result_package}

        except Exception as e:
            print(f"Error during content repurposing workflow: {e}")
            # Return an error structure that the frontend can handle
            # This helps in debugging from the client-side
            return {
                "error": str(e),
                "repurposed_content": {
                    "summary": "An error occurred.",
                    "social_posts": {
                        "twitter": "Error",
                        "linkedin": "Error",
                        "instagram": "Error",
                    },
                    "faq_section": "Error",
                    "entities": {
                        "people": [],
                        "organizations": [],
                        "topics": [],
                    },
                },
            }