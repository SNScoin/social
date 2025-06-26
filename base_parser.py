from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseParser(ABC):
    """Base class for all social media parsers"""
    
    @abstractmethod
    async def parse_url(self, url: str) -> Dict[str, Any]:
        """
        Parse the given URL and return metadata
        
        Args:
            url (str): The URL to parse
            
        Returns:
            Dict[str, Any]: Dictionary containing:
                - title: str
                - views: int
                - likes: int 
                - comments: int
        """
        pass
    
    @abstractmethod
    def validate_url(self, url: str) -> bool:
        """
        Validate if the URL is supported by this parser
        
        Args:
            url (str): The URL to validate
            
        Returns:
            bool: True if URL is valid for this parser
        """
        pass 