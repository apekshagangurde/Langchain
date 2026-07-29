from mcp.server.fastmcp import FastMCP

mcp = FastMCP("text_utils")


@mcp.tool()
def analyze_text(text: str) -> str:
    """Count words and characters in a piece of text, and return it reversed.

    Args:
        text: The text to analyze.
    """
    word_count = len(text.split())
    char_count = len(text)
    reversed_text = text[::-1]
    return (
        f"Words: {word_count}, Characters: {char_count}, Reversed: \"{reversed_text}\""
    )


if __name__ == "__main__":
    mcp.run(transport="stdio")
