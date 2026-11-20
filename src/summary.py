from pathlib import Path
import pandas as pd

def create_summary(scored_path="reports/scored_responses.csv",
                   pairs_path="reports/pairwise_comparison.csv",
                   output_path="reports/summary.txt"):
    scored = pd.read_csv(scored_path)
    pairs = pd.read_csv(pairs_path)
    lines = [
        "AI RESPONSE EVALUATION SUMMARY",
        "=" * 32,
        f"Responses evaluated: {len(scored)}",
        f"Questions with complete A/B pairs: {len(pairs)}",
        f"Mean adjusted quality score: {scored.adjusted_score.mean():.2f}/100",
        f"Responses flagged for hallucination: {int(scored.hallucination_flag.sum())}",
        "",
        "Pairwise preference counts:",
        pairs.preferred_response.value_counts().to_string(),
        "",
        "Note: This report summarizes the supplied demonstration annotations.",
        "It is not a benchmark of any commercial AI model."
    ]
    Path(output_path).write_text("\n".join(lines), encoding="utf-8")
    print(f"Summary saved to {output_path}")

if __name__ == "__main__":
    create_summary()
