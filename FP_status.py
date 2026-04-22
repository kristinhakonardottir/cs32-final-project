import json
import csv

def interactive_matcher():
    # 1. Load the AI-generated weights
    try:
        with open('weights.json', 'r') as f:
            weights_lookup = json.load(f)
    except FileNotFoundError:
        print("❌ Error: Run ai_extractor.py first!")
        return

    # 2. Mocking your Canvas data (replace with your existing parsing logic)
    calendar_assignments = ["Pset 1", "Pset 2", "Final Project Draft", "Lab 1"]
    final_output = []

    print("\n--- INTERACTIVE ASSIGNMENT MATCHING ---")

    for category, weight in weights_lookup.items():
        print(f"\nCategory: {category} (Weight: {weight*100}%)")
        print(f"Detected assignments in calendar: {calendar_assignments}")

        # Prompting the user as requested
        user_input = input(f"Which assignments from the list belong to '{category}'? (Separate by commas): ")

        selected = [name.strip() for name in user_input.split(',')]

        for item in selected:
            if item in calendar_assignments:
                final_output.append({
                    "Assignment": item,
                    "Category": category,
                    "Weight": weight
                })

    # 3. Save to final CSV
    with open('final_planner.csv', 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["Assignment", "Category", "Weight"])
        writer.writeheader()
        writer.writerows(final_output)

    print("\n✅ Final planner saved to final_planner.csv")

if __name__ == "__main__":
    interactive_matcher()
