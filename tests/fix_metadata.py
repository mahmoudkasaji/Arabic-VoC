"""
Fix Channel Metadata for Existing Feedback
Updates existing feedback to include proper source_type metadata
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models_unified import Feedback, FeedbackChannel

def fix_channel_metadata():
    """Update existing feedback to include proper channel metadata"""
    
    with app.app_context():
        # Get all feedback without proper metadata
        feedback_items = db.session.query(Feedback).all()
        
        updated_count = 0
        
        for feedback in feedback_items:
            needs_update = False
            
            # Check if metadata is missing or incomplete
            if not feedback.channel_metadata:
                needs_update = True
                feedback.channel_metadata = {}
            elif not isinstance(feedback.channel_metadata, dict):
                needs_update = True
                feedback.channel_metadata = {}
            elif 'source_type' not in feedback.channel_metadata:
                needs_update = True
            
            if needs_update:
                # Add appropriate metadata based on channel
                if feedback.channel == FeedbackChannel.EMAIL:
                    feedback.channel_metadata.update({
                        'source_type': 'GMAIL_DELIVERY',
                        'delivery_method': 'survey_link',
                        'updated_by': 'metadata_fix_script'
                    })
                elif feedback.channel == FeedbackChannel.WIDGET:
                    feedback.channel_metadata.update({
                        'source_type': 'SIDEBAR_WIDGET',
                        'widget_version': '2.0',
                        'updated_by': 'metadata_fix_script'
                    })
                
                updated_count += 1
                print(f"Updated feedback {feedback.id} ({feedback.channel}) with metadata")
        
        # Commit changes
        db.session.commit()
        
        print(f"\n✅ Updated {updated_count} feedback entries with proper metadata")
        
        # Verify updates
        print("\n🔍 Verification:")
        verified_feedback = db.session.query(Feedback).filter(
            Feedback.channel_metadata['source_type'].astext.isnot(None)
        ).count()
        
        total_feedback = db.session.query(Feedback).count()
        
        print(f"Total feedback: {total_feedback}")
        print(f"With source_type: {verified_feedback}")
        print(f"Success rate: {(verified_feedback/total_feedback*100):.1f}%" if total_feedback > 0 else "No feedback found")

if __name__ == "__main__":
    fix_channel_metadata()