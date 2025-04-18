import requests
from typing import Dict
import re
import os

class SecurityValidator:
    def __init__(self):
        self.vpn_api_key = os.getenv('VPN_DETECTION_API_KEY')
        self.allowed_user_agents = [
            r'Mozilla/.*',
            r'Chrome/.*',
            r'Safari/.*',
            r'Edge/.*',
            r'Firefox/.*'
        ]

    async def check_vpn(self, ip_address: str) -> bool:
        """
        Check if the IP address is a VPN using an external API
        Returns True if VPN is detected
        """
        try:
            # Example using ipapi.co - replace with your preferred VPN detection service
            response = requests.get(f'https://ipapi.co/{ip_address}/json/')
            data = response.json()
            
            # Check for common VPN indicators
            suspicious_indicators = [
                data.get('hosting', False),
                data.get('proxy', False),
                data.get('tor', False),
                data.get('vpn', False)
            ]
            
            return any(suspicious_indicators)
            
        except Exception as e:
            print(f"VPN check error: {e}")
            return False

    def validate_user_agent(self, user_agent: str) -> bool:
        """
        Validate if the user agent is from a legitimate browser
        Returns True if user agent is valid
        """
        if not user_agent:
            return False

        return any(
            re.match(pattern, user_agent)
            for pattern in self.allowed_user_agents
        )

    def validate_request_headers(self, headers: Dict) -> tuple[bool, str]:
        """
        Validate various request headers for security
        Returns (is_valid, message)
        """
        # Check for required headers
        required_headers = ['user-agent', 'origin', 'referer']
        for header in required_headers:
            if header not in headers:
                return False, f"Missing required header: {header}"

        # Validate user agent
        if not self.validate_user_agent(headers['user-agent']):
            return False, "Invalid user agent"

        # Additional header checks can be added here
        return True, "Valid headers"

    async def validate_request(self, headers: Dict, ip_address: str) -> tuple[bool, str]:
        """
        Comprehensive request validation
        Returns (is_valid, message)
        """
        # Validate headers
        headers_valid, headers_message = self.validate_request_headers(headers)
        if not headers_valid:
            return False, headers_message

        # Check for VPN
        if await self.check_vpn(ip_address):
            return False, "VPN usage detected"

        return True, "Request validated successfully"