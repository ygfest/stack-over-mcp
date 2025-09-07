"""
Stack Overflow API client for searching questions and answers.
"""
import requests
from typing import List, Dict, Any, Optional
from urllib.parse import quote
import re


class StackOverflowAPI:
    """Client for interacting with Stack Overflow API."""
    
    BASE_URL = "https://api.stackexchange.com/2.3"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Stack-Over-MCP/1.0'
        })
    
    def _extract_keywords(self, query: str) -> List[str]:
        """
        Extract key terms from a query for fallback searches.
        
        Args:
            query: Original search query
        
        Returns:
            List of important keywords
        """
        # Remove common words and extract meaningful terms
        stop_words = {'how', 'to', 'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'for', 'with', 'by', 'from', 'up', 'about', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'between', 'among', 'can', 'could', 'should', 'would', 'will', 'shall', 'may', 'might', 'must', 'do', 'does', 'did', 'have', 'has', 'had', 'be', 'am', 'is', 'are', 'was', 'were', 'been', 'being', 'get', 'got', 'make', 'made', 'take', 'took', 'give', 'gave', 'come', 'came', 'go', 'went', 'see', 'saw', 'know', 'knew', 'think', 'thought', 'say', 'said', 'tell', 'told', 'become', 'became', 'leave', 'left', 'find', 'found', 'seem', 'seemed', 'turn', 'turned', 'put', 'set', 'move', 'moved', 'right', 'way', 'even', 'back', 'good', 'new', 'first', 'last', 'long', 'great', 'little', 'own', 'other', 'old', 'right', 'big', 'high', 'different', 'small', 'large', 'next', 'early', 'young', 'important', 'few', 'public', 'bad', 'same', 'able'}
        
        # Split query into words and filter
        words = re.findall(r'\b\w+\b', query.lower())
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        return keywords[:5]  # Limit to top 5 keywords
    
    def _extract_technology_terms(self, query: str) -> List[str]:
        """
        Extract technology/framework names that could be used as tags.
        
        Args:
            query: Original search query
        
        Returns:
            List of potential technology tags
        """
        # Common technology terms that are often tags on Stack Overflow
        tech_terms = {
            'python', 'javascript', 'java', 'c#', 'c++', 'php', 'ruby', 'go', 'rust', 'swift', 'kotlin',
            'react', 'vue', 'angular', 'node', 'express', 'django', 'flask', 'spring', 'laravel',
            'mysql', 'postgresql', 'mongodb', 'redis', 'elasticsearch',
            'docker', 'kubernetes', 'aws', 'azure', 'gcp',
            'pandas', 'numpy', 'tensorflow', 'pytorch',
            'airflow', 'spark', 'hadoop', 'kafka',
            'git', 'github', 'gitlab', 'jenkins', 'ci/cd'
        }
        
        query_lower = query.lower()
        found_terms = []
        
        for term in tech_terms:
            if term in query_lower:
                found_terms.append(term)
        
        # Handle special cases
        if 'dag' in query_lower and 'airflow' in query_lower:
            found_terms.append('airflow-scheduler')
        
        return found_terms

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
        # Try different search strategies based on input
        if query and tags:
            # Use advanced search when both query and tags are provided
            return self._search_advanced(query, limit, sort, tags, accepted_only)
        elif tags and not query:
            # Use questions endpoint when only tags are provided
            return self._search_by_tags_only(tags, limit, sort, accepted_only)
        elif query and not tags:
            # Use advanced search for query-only searches
            return self._search_advanced(query, limit, sort, tags, accepted_only)
        else:
            # Fallback to popular questions
            return self._search_by_tags_only(['python'], limit, sort, accepted_only)
    
    def _search_advanced(
        self, 
        query: str, 
        limit: int, 
        sort: str, 
        tags: Optional[List[str]], 
        accepted_only: bool
    ) -> Dict[str, Any]:
        """Use the /search/advanced endpoint for better results."""
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
            response = self.session.get(f"{self.BASE_URL}/search/advanced", params=params)
            response.raise_for_status()
            result = response.json()
            
            # If no results, try fallback searches
            if not result.get('items'):
                result = self._try_fallback_searches(query, limit, sort, tags, accepted_only)
            
            return result
        except requests.RequestException as e:
            return {
                'error': f"API request failed: {str(e)}",
                'items': []
            }
    
    def _search_by_tags_only(
        self, 
        tags: List[str], 
        limit: int, 
        sort: str, 
        accepted_only: bool
    ) -> Dict[str, Any]:
        """Use the /questions endpoint for tag-only searches."""
        params = {
            'order': 'desc',
            'sort': sort,
            'tagged': ';'.join(tags),
            'site': 'stackoverflow',
            'pagesize': min(max(limit, 1), 100),
            'filter': 'withbody'
        }
        
        if accepted_only:
            params['accepted'] = 'True'
        
        try:
            response = self.session.get(f"{self.BASE_URL}/questions", params=params)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            return {
                'error': f"API request failed: {str(e)}",
                'items': []
            }
    
    def _try_fallback_searches(
        self, 
        original_query: str, 
        limit: int, 
        sort: str, 
        original_tags: Optional[List[str]], 
        accepted_only: bool
    ) -> Dict[str, Any]:
        """
        Try multiple fallback search strategies when initial search returns no results.
        
        Args:
            original_query: The original search query
            limit: Maximum results to return
            sort: Sort order
            original_tags: Original tags filter
            accepted_only: Whether to only return accepted answers
        
        Returns:
            Search results from fallback strategies
        """
        fallback_strategies = [
            # Strategy 1: Extract keywords and search with those
            {
                'query': ' '.join(self._extract_keywords(original_query)),
                'tags': original_tags,
                'accepted_only': False  # Relax accepted_only constraint
            },
            # Strategy 2: Use technology terms as tags with broader query
            {
                'query': ' '.join(self._extract_keywords(original_query)),
                'tags': self._extract_technology_terms(original_query) or original_tags,
                'accepted_only': False
            },
            # Strategy 3: Very broad search with just technology tags
            {
                'query': '',
                'tags': self._extract_technology_terms(original_query),
                'accepted_only': False
            },
            # Strategy 4: Single most important keyword
            {
                'query': self._extract_keywords(original_query)[0] if self._extract_keywords(original_query) else original_query.split()[0],
                'tags': None,
                'accepted_only': False
            }
        ]
        
        for strategy in fallback_strategies:
            if not strategy['query'] and not strategy['tags']:
                continue
                
            params = {
                'order': 'desc',
                'sort': sort,
                'q': strategy['query'],
                'site': 'stackoverflow',
                'pagesize': min(max(limit, 1), 100),
                'filter': 'withbody'
            }
            
            if strategy['tags']:
                params['tagged'] = ';'.join(strategy['tags'])
            
            if strategy['accepted_only']:
                params['accepted'] = 'True'
            
            try:
                if strategy['query'] and strategy['tags']:
                    response = self.session.get(f"{self.BASE_URL}/search/advanced", params=params)
                elif strategy['tags'] and not strategy['query']:
                    response = self.session.get(f"{self.BASE_URL}/questions", params=params)
                else:
                    response = self.session.get(f"{self.BASE_URL}/search/advanced", params=params)
                
                response.raise_for_status()
                result = response.json()
                
                if result.get('items'):
                    # Add metadata about which fallback strategy worked
                    result['fallback_used'] = {
                        'original_query': original_query,
                        'fallback_query': strategy['query'],
                        'fallback_tags': strategy['tags']
                    }
                    return result
            except requests.RequestException:
                continue
        
        # If all fallback strategies fail, return empty result
        return {'items': []}
    
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
