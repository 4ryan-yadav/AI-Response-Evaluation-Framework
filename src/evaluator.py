import argparse
from pathlib import Path
import pandas as pd

DIMENSIONS = [
    "factual_accuracy", "relevance", "completeness",
    "instruction_adherence", "clarity"
]

def load_annotations(path):
    df = pd.read_csv(path)
    required = {"question_id", "response_id", "response", *DIMENSIONS, "hallucination_flag"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    for col in DIMENSIONS:
        df[col] = pd.to_numeric(df[col], errors="raise")
        if not df[col].between(1, 5).all():
            raise ValueError(f"{col} must contain scores from 1 to 5.")
    df["hallucination_flag"] = pd.to_numeric(df["hallucination_flag"], errors="raise")
    if not df["hallucination_flag"].isin([0, 1]).all():
        raise ValueError("hallucination_flag must be 0 or 1.")
    return df

def score_responses(df):
    result = df.copy()
    # Equal-weight rubric: each dimension contributes 20% of the total.
    result["quality_score"] = result[DIMENSIONS].mean(axis=1) * 20
    # A flagged hallucination incurs a transparent 10-point penalty.
    result["adjusted_score"] = (result["quality_score"] - 10 * result["hallucination_flag"]).clip(0, 100)
    return result

def compare_pairs(scored):
    rows = []
    for qid, group in scored.groupby("question_id"):
        if len(group) != 2 or set(group["response_id"]) != {"A", "B"}:
            continue
        a = group.loc[group.response_id == "A"].iloc[0]
        b = group.loc[group.response_id == "B"].iloc[0]
        if a.adjusted_score > b.adjusted_score:
            winner = "A"
        elif b.adjusted_score > a.adjusted_score:
            winner = "B"
        else:
            winner = "Tie"
        rows.append({
            "question_id": qid,
            "score_A": round(float(a.adjusted_score), 2),
            "score_B": round(float(b.adjusted_score), 2),
            "preferred_response": winner,
            "score_margin": round(abs(float(a.adjusted_score)-float(b.adjusted_score)), 2)
        })
    return pd.DataFrame(rows)

def main():
    parser = argparse.ArgumentParser(description="Score and compare annotated AI responses.")
    parser.add_argument("--input", default="data/sample_annotations.csv")
    parser.add_argument("--output-dir", default="reports")
    args = parser.parse_args()

    df = load_annotations(args.input)
    scored = score_responses(df)
    comparisons = compare_pairs(scored)
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    scored.to_csv(out / "scored_responses.csv", index=False)
    comparisons.to_csv(out / "pairwise_comparison.csv", index=False)

    print(f"Annotated responses: {len(scored)}")
    print(f"Complete pairs compared: {len(comparisons)}")
    print(f"Average adjusted score: {scored.adjusted_score.mean():.1f}/100")
    print("\nPairwise preferences:")
    print(comparisons["preferred_response"].value_counts().to_string())
    print(f"\nReports saved to: {out.resolve()}")

if __name__ == "__main__":
    main()
