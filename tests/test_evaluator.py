import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from evaluator import score_responses, compare_pairs

def test_score_is_0_to_100_before_penalty():
    data = pd.DataFrame([{
        "question_id":"T1", "response_id":"A", "response":"test",
        "factual_accuracy":5, "relevance":5, "completeness":5,
        "instruction_adherence":5, "clarity":5, "hallucination_flag":0
    }])
    result = score_responses(data)
    assert result.iloc[0].adjusted_score == 100

def test_hallucination_penalty():
    data = pd.DataFrame([{
        "question_id":"T1", "response_id":"A", "response":"test",
        "factual_accuracy":5, "relevance":5, "completeness":5,
        "instruction_adherence":5, "clarity":5, "hallucination_flag":1
    }])
    result = score_responses(data)
    assert result.iloc[0].adjusted_score == 90

def test_pairwise_comparison():
    data = pd.DataFrame([
        {"question_id":"T1","response_id":"A","response":"a","factual_accuracy":5,"relevance":5,"completeness":5,"instruction_adherence":5,"clarity":5,"hallucination_flag":0},
        {"question_id":"T1","response_id":"B","response":"b","factual_accuracy":2,"relevance":2,"completeness":2,"instruction_adherence":2,"clarity":2,"hallucination_flag":0}
    ])
    result = compare_pairs(score_responses(data))
    assert result.iloc[0].preferred_response == "A"
