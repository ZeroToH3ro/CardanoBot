from datetime import datetime

class FormatUtils:
    """Utility class for formatting various data types"""

    @staticmethod
    def format_ada(lovelace: int) -> str:
        """
        Convert lovelace (millionths of ADA) to ADA with proper formatting

        Args:
            lovelace (int): Amount in lovelace (1 ADA = 1,000,000 lovelace)

        Returns:
            str: Formatted string with ADA amount (e.g., "1,234.56")

        Example:
            >>> FormatUtils.format_ada(1234567890)
            '1,234.57'
        """
        try:
            ada_amount = float(lovelace) / 1_000_000
            return f"{ada_amount:,.2f}"
        except (ValueError, TypeError):
            return "0.00"

    @staticmethod
    def format_timestamp(timestamp: int) -> str:
        """
        Convert Unix timestamp to readable date format

        Args:
            timestamp (int): Unix timestamp in seconds

        Returns:
            str: Formatted date string (e.g., "2024-11-30 14:30:00 UTC")

        Example:
            >>> FormatUtils.format_timestamp(1701345600)
            '2024-11-30 14:00:00 UTC'
        """
        try:
            return datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S UTC')
        except (ValueError, TypeError):
            return "Invalid timestamp"

    @staticmethod
    def format_number(number: float, decimals: int = 2) -> str:
        """
        Format number with thousand separators and specified decimal places

        Args:
            number (float): Number to format
            decimals (int): Number of decimal places (default: 2)

        Returns:
            str: Formatted number string

        Example:
            >>> FormatUtils.format_number(1234567.89)
            '1,234,567.89'
        """
        try:
            return f"{float(number):,.{decimals}f}"
        except (ValueError, TypeError):
            return "0.00"

    @staticmethod
    def format_percentage(value: float, decimals: int = 2) -> str:
        """
        Format percentage value with specified decimal places

        Args:
            value (float): Percentage value (e.g., 0.156 for 15.6%)
            decimals (int): Number of decimal places (default: 2)

        Returns:
            str: Formatted percentage string

        Example:
            >>> FormatUtils.format_percentage(0.156)
            '15.60%'
        """
        try:
            return f"{float(value * 100):.{decimals}f}%"
        except (ValueError, TypeError):
            return "0.00%"