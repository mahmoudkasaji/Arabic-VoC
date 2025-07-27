"""
Fix Widget Channel Metadata
Updates widget feedback to include proper source_type metadata structure
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db
from models_unified import Feedback, FeedbackChannel

def fix_widget_metadata():
    """Fix widget feedback metadata structure"""
    
    with app.app_context():
        # Get widget feedback with incomplete metadata
        widget_feedback = db.session.query(Feedback).filter_by(
            channel=FeedbackChannel.WIDGET
        ).all()
        
        updated_count = 0
        
        for feedback in widget_feedback:
            needs_update = False
            
            # Check if metadata needs fixing
            if not feedback.channel_metadata:
                needs_update = True
                feedback.channel_metadata = {}
            elif not isinstance(feedback.channel_metadata, dict):
                needs_update = True
                feedback.channel_metadata = {}
            elif 'source_type' not in feedback.channel_metadata:
                needs_update = True
            elif feedback.channel_metadata.get('source_type') == 'SIDEBAR_WIDGET':
                # Already correct, skip
                continue
            
            if needs_update:
                # Update with proper widget metadata
                feedback.channel_metadata = {
                    'source_type': 'SIDEBAR_WIDGET',
                    'widget_version': '2.0',
                    'widget_position': 'bottom-left',
                    'updated_by': 'widget_metadata_fix'
                }
                
                updated_count += 1
                print(f"Fixed widget feedback {feedback.id} metadata")
        
        # Commit changes
        db.session.commit()
        
        print(f"\n✅ Updated {updated_count} widget feedback entries")
        
        # Verify all widget feedback now has proper metadata
        widget_with_source = db.session.query(Feedback).filter(
            Feedback.channel == FeedbackChannel.WIDGET
        ).all()
        
        proper_metadata_count = 0
        for feedback in widget_with_source:
            if (feedback.channel_metadata and 
                isinstance(feedback.channel_metadata, dict) and
                feedback.channel_metadata.get('source_type') in ['SIDEBAR_WIDGET', 'FOOTER_WIDGET']):
                proper_metadata_count += 1
        
        total_widget = len(widget_with_source)
        print(f"Widget feedback with proper metadata: {proper_metadata_count}/{total_widget}")
        print(f"Widget metadata success rate: {(proper_metadata_count/total_widget*100):.1f}%" if total_widget > 0 else "No widget feedback found")

if __name__ == "__main__":
    fix_widget_metadata()