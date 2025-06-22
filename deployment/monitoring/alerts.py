#!/usr/bin/env python3
"""
Monitoring and alerting system for Arabic VoC Platform
Proactive monitoring with intelligent alerting
"""

import asyncio
import json
import logging
import os
import smtplib
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import aiohttp

from health_check import HealthChecker, HealthCheckResult

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AlertRule:
    """Alert rule configuration"""
    name: str
    condition: str  # "service_unhealthy", "response_time_high", "error_rate_high"
    threshold: float
    duration: int  # seconds
    severity: str  # "critical", "warning", "info"
    channels: List[str]  # ["email", "slack", "webhook"]

@dataclass
class Alert:
    """Alert instance"""
    rule_name: str
    service: str
    severity: str
    message: str
    timestamp: datetime
    resolved: bool = False
    resolution_time: Optional[datetime] = None

class AlertManager:
    """Intelligent alerting system"""
    
    def __init__(self):
        self.alerts = []
        self.alert_history = []
        self.rules = self._load_alert_rules()
        self.health_checker = HealthChecker()
        
        # Configuration
        self.email_config = {
            'smtp_server': os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
            'smtp_port': int(os.getenv('SMTP_PORT', '587')),
            'username': os.getenv('EMAIL_USERNAME'),
            'password': os.getenv('EMAIL_PASSWORD'),
            'from_email': os.getenv('FROM_EMAIL', 'alerts@arabicvoc.com'),
            'to_emails': os.getenv('ALERT_EMAILS', '').split(',')
        }
        
        self.slack_webhook = os.getenv('SLACK_WEBHOOK_URL')
        self.webhook_url = os.getenv('ALERT_WEBHOOK_URL')
    
    def _load_alert_rules(self) -> List[AlertRule]:
        """Load alerting rules configuration"""
        return [
            AlertRule(
                name="service_down",
                condition="service_unhealthy",
                threshold=1,
                duration=60,
                severity="critical",
                channels=["email", "slack"]
            ),
            AlertRule(
                name="high_response_time",
                condition="response_time_high",
                threshold=5.0,
                duration=300,
                severity="warning",
                channels=["email"]
            ),
            AlertRule(
                name="database_slow",
                condition="database_slow",
                threshold=2.0,
                duration=180,
                severity="warning",
                channels=["slack"]
            ),
            AlertRule(
                name="ai_analysis_failing",
                condition="ai_unhealthy",
                threshold=1,
                duration=120,
                severity="critical",
                channels=["email", "slack"]
            ),
            AlertRule(
                name="memory_high",
                condition="memory_high",
                threshold=85.0,
                duration=600,
                severity="warning",
                channels=["email"]
            )
        ]
    
    async def check_alert_conditions(self, health_summary: Dict[str, Any]):
        """Check if any alert conditions are met"""
        new_alerts = []
        
        for rule in self.rules:
            alert = self._evaluate_rule(rule, health_summary)
            if alert:
                new_alerts.append(alert)
        
        # Process new alerts
        for alert in new_alerts:
            await self._trigger_alert(alert)
        
        # Check for resolved alerts
        await self._check_resolved_alerts(health_summary)
    
    def _evaluate_rule(self, rule: AlertRule, health_summary: Dict[str, Any]) -> Optional[Alert]:
        """Evaluate a specific alert rule"""
        checks = health_summary.get('checks', [])
        
        if rule.condition == "service_unhealthy":
            for check in checks:
                if check['status'] == 'unhealthy':
                    # Check if this alert already exists
                    existing = self._find_existing_alert(rule.name, check['service'])
                    if not existing:
                        return Alert(
                            rule_name=rule.name,
                            service=check['service'],
                            severity=rule.severity,
                            message=f"Service {check['service']} is unhealthy: {check['message']}",
                            timestamp=datetime.now()
                        )
        
        elif rule.condition == "response_time_high":
            for check in checks:
                if check['response_time'] > rule.threshold:
                    existing = self._find_existing_alert(rule.name, check['service'])
                    if not existing:
                        return Alert(
                            rule_name=rule.name,
                            service=check['service'],
                            severity=rule.severity,
                            message=f"High response time for {check['service']}: {check['response_time']:.2f}s",
                            timestamp=datetime.now()
                        )
        
        elif rule.condition == "memory_high":
            for check in checks:
                if check['service'] == 'system_resources' and check['details']:
                    memory_percent = check['details'].get('memory_percent', 0)
                    if memory_percent > rule.threshold:
                        existing = self._find_existing_alert(rule.name, check['service'])
                        if not existing:
                            return Alert(
                                rule_name=rule.name,
                                service=check['service'],
                                severity=rule.severity,
                                message=f"High memory usage: {memory_percent:.1f}%",
                                timestamp=datetime.now()
                            )
        
        return None
    
    def _find_existing_alert(self, rule_name: str, service: str) -> Optional[Alert]:
        """Find existing unresolved alert"""
        for alert in self.alerts:
            if alert.rule_name == rule_name and alert.service == service and not alert.resolved:
                return alert
        return None
    
    async def _trigger_alert(self, alert: Alert):
        """Trigger alert through configured channels"""
        logger.warning(f"ALERT: {alert.severity.upper()} - {alert.message}")
        
        self.alerts.append(alert)
        self.alert_history.append(alert)
        
        # Find the rule to get channel configuration
        rule = next((r for r in self.rules if r.name == alert.rule_name), None)
        if not rule:
            return
        
        # Send through configured channels
        tasks = []
        
        if "email" in rule.channels:
            tasks.append(self._send_email_alert(alert))
        
        if "slack" in rule.channels and self.slack_webhook:
            tasks.append(self._send_slack_alert(alert))
        
        if "webhook" in rule.channels and self.webhook_url:
            tasks.append(self._send_webhook_alert(alert))
        
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _send_email_alert(self, alert: Alert):
        """Send alert via email"""
        try:
            if not self.email_config['username'] or not self.email_config['to_emails']:
                logger.warning("Email configuration missing, skipping email alert")
                return
            
            msg = MIMEMultipart()
            msg['From'] = self.email_config['from_email']
            msg['To'] = ', '.join(self.email_config['to_emails'])
            msg['Subject'] = f"[{alert.severity.upper()}] Arabic VoC Platform Alert: {alert.service}"
            
            body = f"""
Alert Details:
- Service: {alert.service}
- Severity: {alert.severity.upper()}
- Message: {alert.message}
- Time: {alert.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC')}
- Rule: {alert.rule_name}

Please investigate this issue promptly.

Platform Health Dashboard: {os.getenv('DASHBOARD_URL', 'https://your-platform.com/health')}
            """.strip()
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(self.email_config['smtp_server'], self.email_config['smtp_port'])
            server.starttls()
            server.login(self.email_config['username'], self.email_config['password'])
            
            text = msg.as_string()
            server.sendmail(self.email_config['from_email'], self.email_config['to_emails'], text)
            server.quit()
            
            logger.info(f"Email alert sent for {alert.service}")
            
        except Exception as e:
            logger.error(f"Failed to send email alert: {e}")
    
    async def _send_slack_alert(self, alert: Alert):
        """Send alert to Slack"""
        try:
            color = {
                "critical": "danger",
                "warning": "warning", 
                "info": "good"
            }.get(alert.severity, "warning")
            
            payload = {
                "text": f"Arabic VoC Platform Alert",
                "attachments": [
                    {
                        "color": color,
                        "fields": [
                            {
                                "title": "Service",
                                "value": alert.service,
                                "short": True
                            },
                            {
                                "title": "Severity",
                                "value": alert.severity.upper(),
                                "short": True
                            },
                            {
                                "title": "Message",
                                "value": alert.message,
                                "short": False
                            },
                            {
                                "title": "Time",
                                "value": alert.timestamp.strftime('%Y-%m-%d %H:%M:%S UTC'),
                                "short": True
                            }
                        ],
                        "footer": "Arabic VoC Monitoring",
                        "ts": int(alert.timestamp.timestamp())
                    }
                ]
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.slack_webhook, json=payload) as response:
                    if response.status == 200:
                        logger.info(f"Slack alert sent for {alert.service}")
                    else:
                        logger.error(f"Slack alert failed: {response.status}")
                        
        except Exception as e:
            logger.error(f"Failed to send Slack alert: {e}")
    
    async def _send_webhook_alert(self, alert: Alert):
        """Send alert to webhook endpoint"""
        try:
            payload = {
                "alert": {
                    "rule_name": alert.rule_name,
                    "service": alert.service,
                    "severity": alert.severity,
                    "message": alert.message,
                    "timestamp": alert.timestamp.isoformat(),
                    "platform": "arabic_voc"
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, json=payload) as response:
                    if response.status in [200, 201, 202]:
                        logger.info(f"Webhook alert sent for {alert.service}")
                    else:
                        logger.error(f"Webhook alert failed: {response.status}")
                        
        except Exception as e:
            logger.error(f"Failed to send webhook alert: {e}")
    
    async def _check_resolved_alerts(self, health_summary: Dict[str, Any]):
        """Check if any alerts have been resolved"""
        checks = health_summary.get('checks', [])
        
        for alert in self.alerts:
            if alert.resolved:
                continue
            
            # Find corresponding health check
            service_check = next((c for c in checks if c['service'] == alert.service), None)
            
            if service_check and service_check['status'] == 'healthy':
                # Alert is resolved
                alert.resolved = True
                alert.resolution_time = datetime.now()
                
                logger.info(f"Alert resolved: {alert.service} - {alert.message}")
                
                # Optionally send resolution notification
                await self._send_resolution_notification(alert)
    
    async def _send_resolution_notification(self, alert: Alert):
        """Send notification when alert is resolved"""
        try:
            if "slack" in self._get_rule_channels(alert.rule_name) and self.slack_webhook:
                payload = {
                    "text": f"✅ Alert Resolved: {alert.service}",
                    "attachments": [
                        {
                            "color": "good",
                            "fields": [
                                {
                                    "title": "Service", 
                                    "value": alert.service,
                                    "short": True
                                },
                                {
                                    "title": "Resolution Time",
                                    "value": alert.resolution_time.strftime('%Y-%m-%d %H:%M:%S UTC'),
                                    "short": True
                                },
                                {
                                    "title": "Duration",
                                    "value": str(alert.resolution_time - alert.timestamp),
                                    "short": True
                                }
                            ]
                        }
                    ]
                }
                
                async with aiohttp.ClientSession() as session:
                    await session.post(self.slack_webhook, json=payload)
                    
        except Exception as e:
            logger.error(f"Failed to send resolution notification: {e}")
    
    def _get_rule_channels(self, rule_name: str) -> List[str]:
        """Get channels for a specific rule"""
        rule = next((r for r in self.rules if r.name == rule_name), None)
        return rule.channels if rule else []
    
    def get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get all active (unresolved) alerts"""
        return [
            {
                "rule_name": alert.rule_name,
                "service": alert.service,
                "severity": alert.severity,
                "message": alert.message,
                "timestamp": alert.timestamp.isoformat(),
                "duration": str(datetime.now() - alert.timestamp)
            }
            for alert in self.alerts
            if not alert.resolved
        ]
    
    def get_alert_summary(self) -> Dict[str, Any]:
        """Get summary of alerting system status"""
        active_alerts = [a for a in self.alerts if not a.resolved]
        
        return {
            "active_alerts": len(active_alerts),
            "total_alerts_today": len([
                a for a in self.alert_history
                if a.timestamp.date() == datetime.now().date()
            ]),
            "critical_alerts": len([a for a in active_alerts if a.severity == "critical"]),
            "warning_alerts": len([a for a in active_alerts if a.severity == "warning"]),
            "alert_rules": len(self.rules),
            "last_check": datetime.now().isoformat()
        }

async def main():
    """Main monitoring loop"""
    logger.info("Starting Arabic VoC Platform monitoring system...")
    
    alert_manager = AlertManager()
    health_checker = HealthChecker()
    
    while True:
        try:
            # Run health checks
            health_summary = await health_checker.run_all_checks()
            
            # Check for alert conditions
            await alert_manager.check_alert_conditions(health_summary)
            
            # Log summary
            alert_summary = alert_manager.get_alert_summary()
            logger.info(f"Monitoring cycle complete - Active alerts: {alert_summary['active_alerts']}")
            
            # Wait before next check
            await asyncio.sleep(60)  # Check every minute
            
        except Exception as e:
            logger.error(f"Monitoring error: {e}")
            await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())