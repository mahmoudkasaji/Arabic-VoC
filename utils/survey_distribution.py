"""
Survey Distribution Engine
Multi-channel survey delivery with intelligent routing
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func

from models.survey_delivery import (
    SurveyCampaign, SurveyDelivery, SurveyTemplate, 
    DeliveryStatus, SurveyStatus, ChannelPreference
)
from models_unified import FeedbackChannel
from utils.email_delivery import EmailDeliveryEngine
from utils.sms_delivery import SMSDeliveryEngine
from utils.whatsapp_delivery import WhatsAppDeliveryEngine
from utils.web_delivery import WebDeliveryEngine

logger = logging.getLogger(__name__)

class SurveyDistributionManager:
    """Main orchestrator for multi-channel survey distribution"""
    
    def __init__(self):
        self.delivery_engines = {
            FeedbackChannel.EMAIL: EmailDeliveryEngine(),
            FeedbackChannel.SMS: SMSDeliveryEngine(),
            FeedbackChannel.WHATSAPP: WhatsAppDeliveryEngine(),
            FeedbackChannel.WEBSITE: WebDeliveryEngine()
        }
        self.channel_optimizer = ChannelOptimizer()
    
    async def distribute_campaign(self, campaign_id: int, db: AsyncSession) -> Dict[str, Any]:
        """
        Distribute survey campaign across configured channels
        """
        try:
            # Get campaign details
            campaign = await self.get_campaign(campaign_id, db)
            if not campaign:
                raise ValueError(f"Campaign {campaign_id} not found")
            
            if campaign.status != SurveyStatus.SCHEDULED:
                raise ValueError(f"Campaign {campaign_id} is not ready for distribution")
            
            # Get target audience
            audience = await self.get_target_audience(campaign.target_audience, db)
            logger.info(f"Distributing campaign {campaign_id} to {len(audience)} recipients")
            
            # Update campaign status
            campaign.status = SurveyStatus.ACTIVE
            campaign.target_count = len(audience)
            await db.commit()
            
            # Create delivery records
            deliveries = await self.create_delivery_records(campaign, audience, db)
            
            # Start distribution process
            distribution_results = await self.execute_distribution(deliveries, db)
            
            # Update campaign metrics
            await self.update_campaign_metrics(campaign, distribution_results, db)
            
            return {
                'campaign_id': campaign_id,
                'target_audience_size': len(audience),
                'deliveries_created': len(deliveries),
                'distribution_status': 'initiated',
                'channels_used': list(set(d.channel for d in deliveries))
            }
            
        except Exception as e:
            logger.error(f"Distribution failed for campaign {campaign_id}: {e}")
            raise
    
    async def get_campaign(self, campaign_id: int, db: AsyncSession) -> Optional[SurveyCampaign]:
        """Get campaign with template"""
        result = await db.execute(
            select(SurveyCampaign)
            .where(SurveyCampaign.id == campaign_id)
        )
        return result.scalar_one_or_none()
    
    async def get_target_audience(self, audience_config: Dict[str, Any], db: AsyncSession) -> List[Dict[str, Any]]:
        """
        Get target audience based on segmentation criteria
        """
        # Mock implementation - in production this would query customer database
        # Example audience configuration:
        # {
        #   "segments": ["high_value_customers", "recent_customers"],
        #   "filters": {
        #     "region": "riyadh",
        #     "language": "ar",
        #     "last_purchase_days": 30
        #   },
        #   "exclude_recent_survey": True
        # }
        
        mock_audience = [
            {
                'customer_id': 'cust_001',
                'name': 'أحمد محمد',
                'email': 'ahmed@example.com',
                'phone': '+966501234567',
                'whatsapp': '+966501234567',
                'language': 'ar',
                'preferred_channel': 'email'
            },
            {
                'customer_id': 'cust_002', 
                'name': 'فاطمة أحمد',
                'email': 'fatima@example.com',
                'phone': '+966507654321',
                'whatsapp': '+966507654321',
                'language': 'ar',
                'preferred_channel': 'whatsapp'
            }
        ]
        
        return mock_audience[:2]  # Return small sample for testing
    
    async def create_delivery_records(
        self, 
        campaign: SurveyCampaign, 
        audience: List[Dict[str, Any]], 
        db: AsyncSession
    ) -> List[SurveyDelivery]:
        """
        Create delivery records with optimized channel selection
        """
        deliveries = []
        
        for recipient in audience:
            # Get optimal channel for this recipient
            optimal_channel = await self.channel_optimizer.get_optimal_channel(
                recipient, campaign.channels_config
            )
            
            # Generate unique delivery token
            delivery_token = self.generate_delivery_token(campaign.id, recipient['customer_id'])
            
            delivery = SurveyDelivery(
                campaign_id=campaign.id,
                recipient_id=recipient['customer_id'],
                recipient_email=recipient.get('email'),
                recipient_phone=recipient.get('phone'),
                recipient_whatsapp=recipient.get('whatsapp'),
                recipient_name=recipient.get('name'),
                channel=optimal_channel,
                delivery_token=delivery_token,
                scheduled_at=datetime.utcnow(),
                channel_metadata={
                    'recipient_preferences': recipient,
                    'optimization_reason': f'Selected {optimal_channel.value} based on preferences'
                }
            )
            
            db.add(delivery)
            deliveries.append(delivery)
        
        await db.commit()
        return deliveries
    
    async def execute_distribution(
        self, 
        deliveries: List[SurveyDelivery], 
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Execute actual survey distribution across channels
        """
        results = {
            'successful_deliveries': 0,
            'failed_deliveries': 0,
            'channels_used': {},
            'errors': []
        }
        
        # Group deliveries by channel for batch processing
        channel_groups = {}
        for delivery in deliveries:
            channel = delivery.channel
            if channel not in channel_groups:
                channel_groups[channel] = []
            channel_groups[channel].append(delivery)
        
        # Process each channel group
        for channel, channel_deliveries in channel_groups.items():
            try:
                engine = self.delivery_engines.get(channel)
                if not engine:
                    logger.warning(f"No delivery engine for channel {channel}")
                    continue
                
                # Execute delivery for this channel
                channel_results = await engine.send_surveys(channel_deliveries, db)
                
                # Update results
                results['channels_used'][channel.value] = {
                    'attempted': len(channel_deliveries),
                    'successful': channel_results.get('successful', 0),
                    'failed': channel_results.get('failed', 0)
                }
                
                results['successful_deliveries'] += channel_results.get('successful', 0)
                results['failed_deliveries'] += channel_results.get('failed', 0)
                
            except Exception as e:
                logger.error(f"Channel {channel} distribution failed: {e}")
                results['errors'].append(f"Channel {channel}: {str(e)}")
                results['failed_deliveries'] += len(channel_deliveries)
        
        return results
    
    async def update_campaign_metrics(
        self, 
        campaign: SurveyCampaign, 
        distribution_results: Dict[str, Any], 
        db: AsyncSession
    ):
        """Update campaign with distribution results"""
        campaign.sent_count = distribution_results['successful_deliveries']
        campaign.updated_at = datetime.utcnow()
        
        await db.commit()
    
    def generate_delivery_token(self, campaign_id: int, customer_id: str) -> str:
        """Generate unique token for survey response tracking"""
        import hashlib
        import secrets
        
        # Create unique token combining campaign, customer, and random element
        data = f"{campaign_id}:{customer_id}:{secrets.token_hex(8)}"
        return hashlib.sha256(data.encode()).hexdigest()[:32]

class ChannelOptimizer:
    """Intelligent channel selection based on customer preferences and historical data"""
    
    async def get_optimal_channel(
        self, 
        recipient: Dict[str, Any], 
        campaign_channels: Dict[str, Any]
    ) -> FeedbackChannel:
        """
        Determine optimal delivery channel for recipient
        """
        # Get customer preferences
        preferred_channel = recipient.get('preferred_channel', 'email')
        
        # Map string to enum
        channel_mapping = {
            'email': FeedbackChannel.EMAIL,
            'sms': FeedbackChannel.SMS,
            'whatsapp': FeedbackChannel.WHATSAPP,
            'website': FeedbackChannel.WEBSITE
        }
        
        # Check if preferred channel is available in campaign
        preferred_enum = channel_mapping.get(preferred_channel, FeedbackChannel.EMAIL)
        
        available_channels = campaign_channels.get('enabled_channels', ['email'])
        if preferred_enum.value in available_channels:
            return preferred_enum
        
        # Fallback to first available channel
        for channel_str in available_channels:
            if channel_str in channel_mapping:
                return channel_mapping[channel_str]
        
        # Final fallback
        return FeedbackChannel.EMAIL
    
    async def analyze_response_patterns(self, customer_id: str) -> Dict[str, float]:
        """
        Analyze historical response patterns for customer
        Returns channel preference scores
        """
        # Mock implementation - in production would analyze historical data
        return {
            'email': 0.75,
            'sms': 0.60,
            'whatsapp': 0.85,
            'website': 0.40
        }

class SurveyResponseCollector:
    """Handles incoming survey responses from all channels"""
    
    async def collect_response(
        self, 
        delivery_token: str, 
        response_data: Dict[str, Any], 
        channel: FeedbackChannel,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        Collect and process survey response
        """
        try:
            # Find delivery record
            delivery = await self.get_delivery_by_token(delivery_token, db)
            if not delivery:
                raise ValueError(f"Invalid delivery token: {delivery_token}")
            
            # Create response record
            from models.survey_delivery import SurveyResponse, ResponseStatus
            
            survey_response = SurveyResponse(
                campaign_id=delivery.campaign_id,
                delivery_id=delivery.id,
                response_token=delivery_token,
                respondent_id=delivery.recipient_id,
                responses=response_data.get('responses', {}),
                completion_status=ResponseStatus.COMPLETED,
                completion_percentage=100.0,
                started_at=datetime.utcnow(),
                completed_at=datetime.utcnow(),
                submission_channel=channel,
                device_info=response_data.get('metadata', {}),
                language_detected=response_data.get('language', 'ar')
            )
            
            # Process Arabic text responses
            processed_responses = await self.process_arabic_responses(
                survey_response.responses
            )
            survey_response.processed_responses = processed_responses
            
            # Calculate satisfaction and NPS scores
            survey_response.satisfaction_score = self.calculate_satisfaction_score(
                survey_response.responses
            )
            survey_response.nps_score = self.extract_nps_score(
                survey_response.responses
            )
            
            db.add(survey_response)
            
            # Update delivery status
            delivery.status = DeliveryStatus.DELIVERED
            delivery.delivered_at = datetime.utcnow()
            
            # Update campaign metrics
            await self.update_campaign_response_metrics(delivery.campaign_id, db)
            
            await db.commit()
            
            return {
                'response_id': survey_response.id,
                'status': 'processed',
                'satisfaction_score': survey_response.satisfaction_score,
                'completion_time': survey_response.response_time_minutes
            }
            
        except Exception as e:
            logger.error(f"Response collection failed: {e}")
            raise
    
    async def get_delivery_by_token(self, token: str, db: AsyncSession) -> Optional[SurveyDelivery]:
        """Find delivery record by token"""
        result = await db.execute(
            select(SurveyDelivery)
            .where(SurveyDelivery.delivery_token == token)
        )
        return result.scalar_one_or_none()
    
    async def process_arabic_responses(self, responses: Dict[str, Any]) -> Dict[str, Any]:
        """Process Arabic text in survey responses"""
        # Use existing Arabic processing pipeline
        from utils.arabic_processor import process_arabic_text
        
        processed = {}
        for question_id, answer in responses.items():
            if isinstance(answer, str) and any('\u0600' <= char <= '\u06FF' for char in answer):
                # Arabic text detected - process it
                processed[question_id] = {
                    'original': answer,
                    'processed': process_arabic_text(answer),
                    'sentiment': await self.analyze_arabic_sentiment(answer)
                }
            else:
                processed[question_id] = {'original': answer}
        
        return processed
    
    async def analyze_arabic_sentiment(self, text: str) -> Dict[str, float]:
        """Analyze sentiment of Arabic text response"""
        # Use existing AI analysis pipeline
        from utils.openai_client import analyze_arabic_feedback
        
        try:
            analysis = await analyze_arabic_feedback(text)
            return {
                'sentiment_score': analysis.get('sentiment_score', 0.0),
                'confidence': analysis.get('confidence_score', 0.0)
            }
        except Exception as e:
            logger.warning(f"Sentiment analysis failed: {e}")
            return {'sentiment_score': 0.0, 'confidence': 0.0}
    
    def calculate_satisfaction_score(self, responses: Dict[str, Any]) -> Optional[float]:
        """Calculate overall satisfaction score from responses"""
        satisfaction_scores = []
        
        for answer in responses.values():
            if isinstance(answer, (int, float)) and 1 <= answer <= 5:
                # Rating question (1-5 scale)
                satisfaction_scores.append(answer / 5.0)  # Normalize to 0-1
            elif isinstance(answer, (int, float)) and 1 <= answer <= 10:
                # NPS-style question (1-10 scale)
                satisfaction_scores.append(answer / 10.0)  # Normalize to 0-1
        
        if satisfaction_scores:
            return sum(satisfaction_scores) / len(satisfaction_scores)
        
        return None
    
    def extract_nps_score(self, responses: Dict[str, Any]) -> Optional[int]:
        """Extract NPS score if present in responses"""
        for answer in responses.values():
            if isinstance(answer, (int, float)) and 0 <= answer <= 10:
                return int(answer)
        return None
    
    async def update_campaign_response_metrics(self, campaign_id: int, db: AsyncSession):
        """Update campaign response count"""
        campaign = await db.get(SurveyCampaign, campaign_id)
        if campaign:
            campaign.response_count += 1
            campaign.updated_at = datetime.utcnow()
            await db.commit()