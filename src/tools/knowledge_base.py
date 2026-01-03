"""Knowledge base search tool - RAG implementation for research papers."""

import logging
from pathlib import Path
from typing import Dict, List

from mcp.types import Tool, TextContent

from ..server.config import settings

logger = logging.getLogger(__name__)


def _load_research_papers() -> Dict[str, str]:
    """Load all markdown research papers from assets directory.

    Returns:
        Dictionary mapping filename to content
    """
    papers: Dict[str, str] = {}
    research_path = Path(settings.research_papers_path)

    if not research_path.exists():
        logger.warning(f"Research papers path does not exist: {research_path}")
        return papers

    for paper_file in research_path.glob("*.md"):
        try:
            content = paper_file.read_text(encoding="utf-8")
            papers[paper_file.name] = content
            logger.debug(f"Loaded research paper: {paper_file.name}")
        except Exception as e:
            logger.error(f"Failed to load {paper_file.name}: {e}")

    return papers


def _simple_search(query: str, papers: Dict[str, str]) -> List[Dict[str, str]]:
    """Perform simple keyword-based search across papers.

    Args:
        query: Search query string
        papers: Dictionary of paper content

    Returns:
        List of matching papers with relevance scores
    """
    results: List[Dict[str, str]] = []
    query_lower = query.lower()
    query_terms = set(query_lower.split())

    for filename, content in papers.items():
        content_lower = content.lower()

        # Calculate simple relevance score
        score = 0
        for term in query_terms:
            score += content_lower.count(term)

        if score > 0:
            # Extract relevant snippet
            lines = content.split("\n")
            relevant_lines: List[str] = []

            for line in lines:
                if any(term in line.lower() for term in query_terms):
                    relevant_lines.append(line.strip())
                    if len(relevant_lines) >= 5:  # Limit snippet size
                        break

            snippet = "\n".join(relevant_lines) if relevant_lines else content[:500]

            results.append({
                "filename": filename,
                "score": str(score),
                "snippet": snippet,
                "full_content": content
            })

    # Sort by relevance score
    results.sort(key=lambda x: int(x["score"]), reverse=True)
    return results[:3]  # Return top 3 results


async def search_knowledge_base(query: str) -> List[TextContent]:
    """Search the knowledge base for relevant research papers.

    This is a mock RAG implementation that performs keyword-based search
    across markdown files in the research papers directory.

    Args:
        query: Search query string

    Returns:
        List of TextContent with search results
    """
    logger.info(f"Searching knowledge base for: {query}")

    # Load all research papers
    papers = _load_research_papers()

    if not papers:
        return [
            TextContent(
                type="text",
                text="No research papers found. Please ensure papers are available in the research directory."
            )
        ]

    # Perform search
    results = _simple_search(query, papers)

    if not results:
        return [
            TextContent(
                type="text",
                text=f"No results found for query: '{query}'\n\nAvailable papers: {', '.join(papers.keys())}"
            )
        ]

    # Format results
    response_text = f"Found {len(results)} relevant research paper(s) for '{query}':\n\n"

    for i, result in enumerate(results, 1):
        response_text += f"## Result {i}: {result['filename']}\n"
        response_text += f"**Relevance Score:** {result['score']}\n\n"
        response_text += "**Relevant Excerpts:**\n"
        response_text += f"{result['snippet']}\n\n"
        response_text += "---\n\n"

    response_text += "\n**Full Content of Top Result:**\n\n"
    response_text += results[0]["full_content"]

    return [TextContent(type="text", text=response_text)]


# Tool definition for MCP protocol
search_knowledge_base_tool = Tool(
    name="search_knowledge_base",
    description=(
        "Search the quantitative finance knowledge base for research papers and strategies. "
        "Returns relevant excerpts from academic papers on topics like momentum, mean reversion, "
        "volatility trading, pairs trading, and other quantitative strategies. "
        "Use this to get theoretical background and implementation guidance for trading strategies."
    ),
    inputSchema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query (e.g., 'momentum strategy', 'mean reversion', 'volatility trading')"
            }
        },
        "required": ["query"]
    }
)
