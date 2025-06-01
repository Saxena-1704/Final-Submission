from agents.classifier_agent import classify_and_route
import os

if __name__ == "__main__":
    input_folder = "input_samples"
    all_results = []

    for filename in os.listdir(input_folder):
        file_path = os.path.join(input_folder, filename)

        if os.path.isfile(file_path):
            result = classify_and_route(file_path)
            print(f"\nResult for {result['filename']}:\n", result)