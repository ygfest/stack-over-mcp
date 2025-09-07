"""
Stack Over MCP - An MCP server for searching Stack Overflow.

This server provides tools to search Stack Overflow questions and get detailed
information about specific questions and their answers.
"""
import asyncio
from typing import List, Dict, Any, Optional
from fastmcp import FastMCP
from stack_api import StackOverflowAPI


# Initialize the MCP server
mcp = FastMCP("Stack Over MCP")

# Initialize Stack Overflow API client
stack_api = StackOverflowAPI()


@mcp.tool()
def search_stackoverflow(
    query: str,
    limit: int = 10,
    sort: str = "relevance",
    tags: Optional[List[str]] = None,
    accepted_only: bool = False
) -> List[Dict[str, Any]]:
    """
    Search Stack Overflow for questions related to your query.
    
    This tool searches Stack Overflow's database of programming questions and answers,
    helping you find real-world solutions to coding problems.
    
    Args:
        query: The search query (e.g., "python list comprehension", "react hooks error")
        limit: Maximum number of results to return (1-100, default: 10)
        sort: Sort results by "relevance", "activity", "votes", or "creation" (default: "relevance")
        tags: Optional list of tags to filter by (e.g., ["python", "pandas"])
        accepted_only: If True, only return questions that have accepted answers (default: False)
    
    Returns:
        List of Stack Overflow questions with metadata including:
        - question_id: Unique identifier for the question
        - title: Question title
        - score: Community score (upvotes - downvotes)
        - view_count: Number of times the question was viewed
        - answer_count: Number of answers posted
        - is_answered: Whether the question has any answers
        - has_accepted_answer: Whether an answer was accepted by the question author
        - tags: Programming language/technology tags
        - link: Direct URL to the Stack Overflow question
        - body_preview: First 300 characters of the question body
    """
    try:
        # Search Stack Overflow
        results = stack_api.search_questions(
            query=query,
            limit=limit,
            sort=sort,
            tags=tags,
            accepted_only=accepted_only
        )
        
        # Format and return results
        formatted_results = stack_api.format_search_results(results)
        
        if not formatted_results:
            return [{
                'message': f'No results found for query: "{query}"',
                'suggestion': 'Try using different keywords, removing tag filters, or using broader search terms'
            }]
        
        # Add fallback information if used
        if 'fallback_used' in results:
            fallback_info = results['fallback_used']
            formatted_results.insert(0, {
                'info': f'Used fallback search strategy',
                'original_query': fallback_info['original_query'],
                'fallback_query': fallback_info['fallback_query'],
                'fallback_tags': fallback_info.get('fallback_tags'),
                'note': 'Results below are from a modified search to find relevant content'
            })
        
        return formatted_results
        
    except Exception as e:
        return [{
            'error': f'Search failed: {str(e)}',
            'query': query
        }]


@mcp.tool()
def get_question_details(question_id: int, include_answers: bool = True) -> Dict[str, Any]:
    """
    Get detailed information about a specific Stack Overflow question.
    
    Use this tool when you want to dive deeper into a specific question found
    through search_stackoverflow, or when you have a Stack Overflow question ID.
    
    Args:
        question_id: The Stack Overflow question ID (from search results or URL)
        include_answers: Whether to include answers in the response (default: True)
    
    Returns:
        Dictionary containing detailed question information and optionally answers:
        - question: Full question details including complete body text
        - answers: List of answers if include_answers is True, sorted by votes
        - answer_count: Total number of answers
        - top_answer: The highest-voted answer (if any)
        - accepted_answer: The accepted answer (if any)
    """
    try:
        if not include_answers:
            return {
                'message': f'Question details for ID {question_id}',
                'link': f'https://stackoverflow.com/questions/{question_id}',
                'note': 'Use include_answers=True to get full details with answers'
            }
        
        # Get question answers
        answers_data = stack_api.get_question_with_answers(question_id)
        
        if 'error' in answers_data:
            return {
                'error': answers_data['error'],
                'question_id': question_id,
                'link': f'https://stackoverflow.com/questions/{question_id}'
            }
        
        answers = answers_data.get('items', [])
        
        # Format answers
        formatted_answers = []
        accepted_answer = None
        top_answer = None
        
        for answer in answers:
            formatted_answer = {
                'answer_id': answer.get('answer_id'),
                'score': answer.get('score', 0),
                'is_accepted': answer.get('is_accepted', False),
                'creation_date': answer.get('creation_date'),
                'last_activity_date': answer.get('last_activity_date'),
                'body': stack_api._clean_html(answer.get('body', '')),
                'author': answer.get('owner', {}).get('display_name', 'Anonymous')
            }
            
            formatted_answers.append(formatted_answer)
            
            # Track accepted and top answers
            if formatted_answer['is_accepted']:
                accepted_answer = formatted_answer
            
            if not top_answer or formatted_answer['score'] > top_answer['score']:
                top_answer = formatted_answer
        
        return {
            'question_id': question_id,
            'link': f'https://stackoverflow.com/questions/{question_id}',
            'answer_count': len(formatted_answers),
            'answers': formatted_answers,
            'accepted_answer': accepted_answer,
            'top_answer': top_answer if top_answer and top_answer['score'] > 0 else None
        }
        
    except Exception as e:
        return {
            'error': f'Failed to get question details: {str(e)}',
            'question_id': question_id,
            'link': f'https://stackoverflow.com/questions/{question_id}'
        }


@mcp.tool()
def search_by_tags(
    tags: List[str],
    limit: int = 10,
    sort: str = "votes",
    min_score: int = 0
) -> List[Dict[str, Any]]:
    """
    Search Stack Overflow questions by specific programming tags.
    
    This tool helps you find highly-rated questions and solutions for specific
    technologies, programming languages, or frameworks.
    
    Args:
        tags: List of tags to search for (e.g., ["python", "pandas"], ["javascript", "react"])
        limit: Maximum number of results to return (1-100, default: 10)
        sort: Sort by "votes", "activity", "creation", or "relevance" (default: "votes")
        min_score: Minimum score threshold for questions (default: 0)
    
    Returns:
        List of highly-rated Stack Overflow questions for the specified tags
    """
    try:
        # Search with empty query but specific tags
        results = stack_api.search_questions(
            query="",  # Empty query to focus on tags
            limit=limit,
            sort=sort,
            tags=tags
        )
        
        formatted_results = stack_api.format_search_results(results)
        
        # Filter by minimum score if specified
        if min_score > 0:
            formatted_results = [
                result for result in formatted_results 
                if result.get('score', 0) >= min_score
            ]
        
        if not formatted_results:
            return [{
                'message': f'No results found for tags: {", ".join(tags)}',
                'suggestion': f'Try different tags or lower the min_score (currently {min_score})'
            }]
        
        return formatted_results
        
    except Exception as e:
        return [{
            'error': f'Tag search failed: {str(e)}',
            'tags': tags
        }]


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
