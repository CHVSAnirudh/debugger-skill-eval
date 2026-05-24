import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from buggy import Feature, build_predicates, evaluate, user_bucket


def test_predicates_independent_thresholds():
    features = [Feature("a", 10), Feature("b", 50), Feature("c", 90)]
    preds = build_predicates(features)
    # bucket = 30: a should be False (30 >= 10), b/c True (30 < 50, 30 < 90)
    assert preds[0](30) is False
    assert preds[1](30) is True
    assert preds[2](30) is True


def test_predicates_at_boundary():
    features = [Feature("a", 50)]
    preds = build_predicates(features)
    assert preds[0](49) is True
    assert preds[0](50) is False
    assert preds[0](51) is False


def test_evaluate_three_features():
    features = [Feature("a", 10), Feature("b", 50), Feature("c", 90)]

    class FakeUser:
        pass

    # Inject a known bucket by patching user_bucket — we know the math: just test evaluate against
    # a few real user_ids and check the result is consistent with the predicates directly.
    for uid in ["alice", "bob", "carol", "dave", "eve"]:
        bucket = user_bucket(uid)
        expected = {
            "a": bucket < 10,
            "b": bucket < 50,
            "c": bucket < 90,
        }
        assert evaluate(uid, features) == expected, f"user={uid} bucket={bucket}"


def test_one_feature():
    feats = [Feature("only", 25)]
    preds = build_predicates(feats)
    assert preds[0](10) is True
    assert preds[0](40) is False


def test_features_with_extreme_thresholds():
    feats = [Feature("none", 0), Feature("all", 100)]
    preds = build_predicates(feats)
    for b in [0, 50, 99]:
        assert preds[0](b) is False
        assert preds[1](b) is True
