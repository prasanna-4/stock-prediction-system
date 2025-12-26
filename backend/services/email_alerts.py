"""
Email Alert Service
Sends alerts for high-confidence stock predictions
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class EmailAlertService:
    """
    Service for sending email alerts about stock predictions
    """
    
    def __init__(self, 
                 smtp_host: str = "smtp.gmail.com",
                 smtp_port: int = 587,
                 sender_email: str = None,
                 sender_password: str = None):
        """
        Initialize email service
        
        Args:
            smtp_host: SMTP server host
            smtp_port: SMTP server port
            sender_email: Email address to send from
            sender_password: Email password or app password
        """
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.sender_email = sender_email
        self.sender_password = sender_password
        
    def send_alert(self, recipient_email: str, subject: str, body_html: str) -> bool:
        """
        Send an email alert
        
        Args:
            recipient_email: Recipient email address
            subject: Email subject
            body_html: HTML body content
            
        Returns:
            True if successful, False otherwise
        """
        if not self.sender_email or not self.sender_password:
            logger.warning("Email credentials not configured")
            return False
        
        try:
            # Create message
            message = MIMEMultipart('alternative')
            message['From'] = self.sender_email
            message['To'] = recipient_email
            message['Subject'] = subject
            
            # Add HTML body
            html_part = MIMEText(body_html, 'html')
            message.attach(html_part)
            
            # Connect and send
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)
            
            logger.info(f"Alert sent successfully to {recipient_email}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email alert: {e}")
            return False
    
    def send_high_confidence_alerts(self, 
                                    predictions: List[Dict], 
                                    recipient_email: str,
                                    min_confidence: float = 0.7) -> bool:
        """
        Send alerts for high-confidence predictions
        
        Args:
            predictions: List of prediction dictionaries
            recipient_email: Email to send alerts to
            min_confidence: Minimum confidence threshold
            
        Returns:
            True if successful
        """
        # Filter high-confidence predictions
        high_conf = [p for p in predictions if p['confidence'] >= min_confidence]
        
        if not high_conf:
            logger.info("No high-confidence predictions to alert about")
            return True
        
        # Create email content
        subject = f"🚀 {len(high_conf)} High-Confidence Stock Signals - {datetime.now().strftime('%Y-%m-%d')}"
        
        body_html = self._create_alert_html(high_conf)
        
        return self.send_alert(recipient_email, subject, body_html)
    
    def _create_alert_html(self, predictions: List[Dict]) -> str:
        """Create HTML email body for predictions"""
        
        # Sort by confidence
        predictions_sorted = sorted(predictions, key=lambda x: x['confidence'], reverse=True)
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    background-color: #f3f4f6;
                    padding: 20px;
                }}
                .container {{
                    max-width: 800px;
                    margin: 0 auto;
                    background: white;
                    border-radius: 12px;
                    padding: 30px;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                }}
                h1 {{
                    color: #667eea;
                    margin-bottom: 10px;
                }}
                .subtitle {{
                    color: #6b7280;
                    margin-bottom: 30px;
                }}
                .prediction {{
                    background: #f9fafb;
                    border-left: 4px solid #10b981;
                    padding: 20px;
                    margin-bottom: 20px;
                    border-radius: 8px;
                }}
                .prediction.down {{
                    border-left-color: #ef4444;
                }}
                .header {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 15px;
                }}
                .symbol {{
                    font-size: 1.5em;
                    font-weight: bold;
                    color: #667eea;
                }}
                .confidence {{
                    background: #10b981;
                    color: white;
                    padding: 5px 15px;
                    border-radius: 20px;
                    font-weight: bold;
                }}
                .details {{
                    display: grid;
                    grid-template-columns: repeat(2, 1fr);
                    gap: 15px;
                    margin-top: 15px;
                }}
                .detail {{
                    display: flex;
                    flex-direction: column;
                }}
                .detail-label {{
                    color: #6b7280;
                    font-size: 0.85em;
                    margin-bottom: 5px;
                }}
                .detail-value {{
                    font-weight: 600;
                    color: #1f2937;
                }}
                .up {{
                    color: #10b981;
                }}
                .down {{
                    color: #ef4444;
                }}
                .footer {{
                    margin-top: 30px;
                    padding-top: 20px;
                    border-top: 1px solid #e5e7eb;
                    color: #6b7280;
                    font-size: 0.9em;
                    text-align: center;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🚀 High-Confidence Stock Signals</h1>
                <p class="subtitle">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                
                <p>We've identified <strong>{len(predictions_sorted)}</strong> high-confidence trading opportunities:</p>
        """
        
        for pred in predictions_sorted:
            direction_class = pred['direction']
            direction_symbol = '📈' if pred['direction'] == 'up' else '📉'
            
            html += f"""
                <div class="prediction {direction_class}">
                    <div class="header">
                        <span class="symbol">{pred['symbol']}</span>
                        <span class="confidence">{pred['confidence']*100:.1f}%</span>
                    </div>
                    
                    <div style="margin-bottom: 10px;">
                        <strong class="{direction_class}">{direction_symbol} {pred['direction'].upper()}</strong> • 
                        {pred['prediction_type'].title()} Trade
                    </div>
                    
                    <div class="details">
                        <div class="detail">
                            <span class="detail-label">Current Price</span>
                            <span class="detail-value">${pred['current_price']:.2f}</span>
                        </div>
                        <div class="detail">
                            <span class="detail-label">Target Price</span>
                            <span class="detail-value up">${pred['target_price']:.2f}</span>
                        </div>
                        <div class="detail">
                            <span class="detail-label">Entry Zone</span>
                            <span class="detail-value">${pred['entry_price_low']:.2f} - ${pred['entry_price_high']:.2f}</span>
                        </div>
                        <div class="detail">
                            <span class="detail-label">Stop Loss</span>
                            <span class="detail-value down">${pred['stop_loss_price']:.2f}</span>
                        </div>
                        <div class="detail">
                            <span class="detail-label">Predicted Growth</span>
                            <span class="detail-value {direction_class}">{pred['predicted_growth_percent']:+.2f}%</span>
                        </div>
                        <div class="detail">
                            <span class="detail-label">Target Date</span>
                            <span class="detail-value">{pred['target_date']}</span>
                        </div>
                    </div>
                </div>
            """
        
        html += """
                <div class="footer">
                    <p><strong>⚠️ Disclaimer:</strong> These are AI-generated predictions for informational purposes only. 
                    Always do your own research and consult with a financial advisor before making investment decisions.</p>
                    <p>Stock Prediction System v1.0 • Powered by Machine Learning</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html


# Example usage
if __name__ == "__main__":
    # Demo: Create sample predictions and show HTML
    sample_predictions = [
        {
            'symbol': 'AAPL',
            'direction': 'up',
            'confidence': 0.85,
            'prediction_type': 'swing',
            'current_price': 180.50,
            'target_price': 195.00,
            'entry_price_low': 179.00,
            'entry_price_high': 182.00,
            'stop_loss_price': 171.50,
            'predicted_growth_percent': 8.03,
            'target_date': '2025-01-03'
        }
    ]
    
    service = EmailAlertService()
    html = service._create_alert_html(sample_predictions)
    
    print("Sample Email HTML:")
    print(html)