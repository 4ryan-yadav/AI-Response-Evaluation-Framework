import pandas as pd
import random
from pathlib import Path
def randomize_labels():
    base_dir = Path(__file__).resolve().parent.parent
    input_file = base_dir / "data" / "sample_annotations.csv"
    output_file = base_dir / "data" / "sample_annotations_randomized.csv"
    if not input_file.exists():
        print("Original dataset not found!")
        return
    df = pd.read_csv(input_file)
    rng = random.Random(42)
    for question_id, group in df.groupby("question_id"):
        if len(group) != 2:
            continue
        if rng.choice([True, False]):
            idx = group.index.tolist()
            df.loc[idx, "response_id"] = (
                df.loc[idx, "response_id"]
                .map({"A": "B", "B": "A"})
            )
    df.to_csv(output_file, index=False)
    print("Randomization completed!")
    print(f"Total responses: {len(df)}")
    print(f"Output created: {output_file}")
if __name__ == "__main__":
    randomize_labels()