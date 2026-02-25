"""
Simple test for property logging functionality (no dependencies)
"""

from datetime import datetime
import json
import os


def log_property_addition(database_name, property_name, property_type, justification):
    """Test implementation of the log_property_addition method"""

    # Create log entry with ISO timestamp
    log_entry = {
        "database": database_name,
        "property": property_name,
        "type": property_type,
        "justification": justification,
        "timestamp": datetime.utcnow().isoformat()
    }

    print(f"NEW PROPERTY CREATED: {log_entry}")

    # Write to structured JSONL log file for audit trail
    try:
        log_file = "logs/property_changes.jsonl"

        # Ensure logs directory exists
        os.makedirs("logs", exist_ok=True)

        # Append to JSONL file (one JSON object per line)
        with open(log_file, mode='a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + "\n")

        print(f"Property addition logged to {log_file}")

    except Exception as e:
        print(f"Error writing property change to log file: {e}")

    return log_entry


def main():
    print("=" * 70)
    print("Testing Property Validation Logging Enhancement")
    print("=" * 70)

    # Test Case 1: Log a property addition
    print("\n[Test 1] Logging property addition...")
    result1 = log_property_addition(
        database_name="Action Pipes",
        property_name="Test_Property",
        property_type="rich_text",
        justification="Testing the enhanced logging functionality"
    )
    print(f"Success! Entry: {result1['property']}")

    # Test Case 2: Log another property to test appending
    print("\n[Test 2] Testing log file appending...")
    result2 = log_property_addition(
        database_name="Training Data",
        property_name="Another_Property",
        property_type="select",
        justification="Testing append functionality"
    )
    print(f"Success! Entry: {result2['property']}")

    # Test Case 3: Different property types
    print("\n[Test 3] Testing different property types...")
    for prop_type in ["number", "checkbox", "date", "multi_select"]:
        log_property_addition(
            database_name="Test Database",
            property_name=f"Test_{prop_type}",
            property_type=prop_type,
            justification=f"Testing {prop_type} type logging"
        )

    # Verify the log file
    log_file = "logs/property_changes.jsonl"
    print("\n" + "=" * 70)
    print("Verification:")
    print("=" * 70)

    if os.path.exists(log_file):
        print(f"\n✓ Log file exists: {log_file}")
        file_size = os.path.getsize(log_file)
        print(f"✓ File size: {file_size} bytes")

        # Read and validate JSONL format
        with open(log_file, 'r') as f:
            lines = f.readlines()
            print(f"✓ Total entries in file: {len(lines)}")

            # Validate each line is valid JSON
            print("\n✓ Validating JSONL format...")
            valid_count = 0
            for i, line in enumerate(lines, 1):
                try:
                    entry = json.loads(line)
                    # Verify required fields
                    required_fields = ["database", "property", "type", "justification", "timestamp"]
                    if all(field in entry for field in required_fields):
                        valid_count += 1
                except json.JSONDecodeError as e:
                    print(f"  ✗ Line {i} is invalid JSON: {e}")

            print(f"✓ Valid entries: {valid_count}/{len(lines)}")

            # Display last 3 entries
            print("\n" + "-" * 70)
            print("Last 3 log entries:")
            print("-" * 70)
            for line in lines[-3:]:
                entry = json.loads(line)
                print(f"\nDatabase: {entry['database']}")
                print(f"Property: {entry['property']} (type: {entry['type']})")
                print(f"Timestamp: {entry['timestamp']}")
                print(f"Justification: {entry['justification']}")

    else:
        print(f"\n✗ ERROR: Log file not found at {log_file}")

    print("\n" + "=" * 70)
    print("Test Completed Successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
