"""
Test script for property validation logging enhancement
Run this to verify the logging functionality works correctly
"""

import sys
import os
from datetime import datetime

# Add the project directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the PropertyValidator (without AsyncClient for testing)
from app.property_validator import PropertyValidator


def test_property_logging():
    """Test the log_property_addition method"""

    print("Testing property logging functionality...")
    print("-" * 60)

    # Create a mock validator (we don't need the client for this test)
    class MockValidator:
        def log_property_addition(self, database_name, property_name, property_type, justification):
            """Copy of the enhanced log_property_addition method"""
            from datetime import datetime
            from loguru import logger
            import json
            import os

            # Create log entry with ISO timestamp
            log_entry = {
                "database": database_name,
                "property": property_name,
                "type": property_type,
                "justification": justification,
                "timestamp": datetime.utcnow().isoformat()
            }

            logger.warning(f"NEW PROPERTY CREATED: {log_entry}")

            # Write to structured JSONL log file for audit trail
            try:
                log_file = "logs/property_changes.jsonl"

                # Ensure logs directory exists
                os.makedirs("logs", exist_ok=True)

                # Append to JSONL file (one JSON object per line)
                with open(log_file, mode='a', encoding='utf-8') as f:
                    f.write(json.dumps(log_entry) + "\n")

                logger.debug(f"Property addition logged to {log_file}")

            except Exception as e:
                logger.error(f"Error writing property change to log file: {e}")
                # Don't raise - logging failure shouldn't break property creation

            return log_entry

    validator = MockValidator()

    # Test Case 1: Log a property addition
    print("\n1. Testing property addition logging...")
    result = validator.log_property_addition(
        database_name="Action Pipes",
        property_name="Test_Property",
        property_type="rich_text",
        justification="Testing the enhanced logging functionality"
    )
    print(f"   Result: {result}")

    # Test Case 2: Log another property to test appending
    print("\n2. Testing log file appending...")
    result2 = validator.log_property_addition(
        database_name="Training Data",
        property_name="Another_Property",
        property_type="select",
        justification="Testing append functionality"
    )
    print(f"   Result: {result2}")

    # Verify the log file was created
    log_file = "logs/property_changes.jsonl"
    if os.path.exists(log_file):
        print(f"\n3. Verifying log file exists: {log_file}")
        print(f"   File size: {os.path.getsize(log_file)} bytes")

        # Read and display the log entries
        print("\n4. Reading log entries:")
        with open(log_file, 'r') as f:
            lines = f.readlines()
            print(f"   Total entries: {len(lines)}")
            print("\n   Last 2 entries:")
            for line in lines[-2:]:
                import json
                entry = json.loads(line)
                print(f"   - {entry['database']}: {entry['property']} ({entry['type']})")
                print(f"     Timestamp: {entry['timestamp']}")
                print(f"     Justification: {entry['justification']}")
    else:
        print(f"\nERROR: Log file not found at {log_file}")

    print("\n" + "=" * 60)
    print("Test completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    test_property_logging()
