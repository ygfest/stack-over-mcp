"""
Stack Overflow API client for searching questions and answers.
"""
import requests
from typing import List, Dict, Any, Optional
from urllib.parse import quote


class StackOverflowAPI:
    """Client for interacting with Stack Overflow API."""
    
    BASE_URL = "https://api.stackexchange.com/2.3"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Stack-Over-MCP/1.0'
        })
    
    def search_questions(
        self, 
        query: str, 
        limit: int = 10,
        sort: str = "relevance",
        tags: Optional[List[str]] = None,
        accepted_only: bool = False
    ) -> Dict[str, Any]:
        """
        Search Stack Overflow questions.
        
        Args:
            query: Search query string
            limit: Maximum number of results (1-100)
            sort: Sort order (relevance, activity, votes, creation)
            tags: List of tags to filter by
            accepted_only: Only return questions with accepted answers
        
        Returns:
            Dictionary containing search results
        """
        params = {
            'order': 'desc',
            'sort': sort,
            'q': query,
            'site': 'stackoverflow',
            'pagesize': min(max(limit, 1), 100),
            'filter': 'withbody'
        }
        
        if tags:
            params['tagged'] = ';'.join(tags)
        
        if accepted_only:
            params['accepted'] = 'True'
        
        try:
            response = self.session.get(f"{self.BASE_URL}/search", params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {
                'error': f"API request failed: {str(e)}",
                'items': []
            }
    
    def get_question_with_answers(self, question_id: int) -> Dict[str, Any]:
        """
        Get a specific question with its answers.
        
        Args:
            question_id: Stack Overflow question ID
        
        Returns:
            Dictionary containing question and answers
        """
        params = {
            'order': 'desc',
            'sort': 'votes',
            'site': 'stackoverflow',
            'filter': 'withbody'
        }
        
        try:
            response = self.session.get(
                f"{self.BASE_URL}/questions/{question_id}/answers", 
                params=params
            )
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {
                'error': f"API request failed: {str(e)}",
                'items': []
            }
    
    def format_search_results(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Format search results for better readability.
        
        Args:
            results: Raw API response
        
        Returns:
            List of formatted question dictionaries
        """
        if 'error' in results:
            return [{'error': results['error']}]
        
        formatted = []
        for item in results.get('items', []):
            formatted_item = {
                'question_id': item.get('question_id'),
                'title': item.get('title', 'No title'),
                'score': item.get('score', 0),
                'view_count': item.get('view_count', 0),
                'answer_count': item.get('answer_count', 0),
                'is_answered': item.get('is_answered', False),
                'has_accepted_answer': item.get('accepted_answer_id') is not None,
                'tags': item.get('tags', []),
                'creation_date': item.get('creation_date'),
                'last_activity_date': item.get('last_activity_date'),
                'link': item.get('link', ''),
                'body_preview': self._clean_html(item.get('body', ''))[:300] + '...' if item.get('body') else 'No preview available'
            }
            formatted.append(formatted_item)
        
        return formatted
    
    def _clean_html(self, html_text: str) -> str:
        """
        Basic HTML tag removal for preview text.
        
        Args:
            html_text: HTML text to clean
        
        Returns:
            Cleaned text
        """
        import re
        # Remove HTML tags
        clean = re.sub('<[^<]+?>', '', html_text)
        # Replace common HTML entities
        clean = clean.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
        # Remove extra whitespace
        clean = ' '.join(clean.split())
        return clean
