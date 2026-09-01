"""Official evaluation metrics for KuaiRand-Pure recommendation ranking.

Metrics:
  - GAUC: Group AUC within each user with 0 < positives < impressions, weighted by number of positives.
  - nDCG@5: nDCG at rank 5 per user (zero-positive users contribute 0.0).
  - primary: mean(GAUC, nDCG@5).
"""
import math
import collections
import numpy as np


def auc_score(labels, scores):
    """Mann-Whitney U with tie correction, equivalent to sklearn.metrics.roc_auc_score."""
    pairs = sorted(zip(scores, labels))
    ranks = [0.0] * len(pairs)
    i = 0
    while i < len(pairs):
        j = i
        while j + 1 < len(pairs) and pairs[j + 1][0] == pairs[i][0]:
            j += 1
        avg = (i + j) / 2.0 + 1.0
        for k in range(i, j + 1):
            ranks[k] = avg
        i = j + 1
    npos = sum(l for _, l in pairs)
    nneg = len(pairs) - npos
    if npos == 0 or nneg == 0:
        return 0.5
    srank = sum(r for r, (_, l) in zip(ranks, pairs) if l == 1)
    return (srank - npos * (npos + 1) / 2.0) / (npos * nneg)


def ndcg_at_k(labels, k=5):
    """Labels ordered in descending order of predicted score."""
    disc = [math.log2(i + 2) for i in range(k)]
    dcg = sum(((2 ** t) - 1) / disc[i] for i, t in enumerate(labels[:k]))
    ideal = sorted(labels, reverse=True)[:k]
    idcg = sum(((2 ** t) - 1) / disc[i] for i, t in enumerate(ideal))
    return 0.0 if idcg == 0 else dcg / idcg


def evaluate(user_ids, labels, scores, k=5):
    """Compute official benchmark metrics on user_ids, labels, and scores.

    Returns dict with keys: 'GAUC', 'nDCG@5', 'primary', 'users', 'rows'.
    """
    byu = collections.defaultdict(list)
    for u, y, s in zip(user_ids, labels, scores):
        byu[u].append((float(s), int(y)))
    gnum = gden = 0.0
    nd = []
    for u, lst in byu.items():
        lst.sort(key=lambda x: -x[0])
        labs = [y for _, y in lst]
        npos = sum(labs)
        if 0 < npos < len(labs):
            gnum += npos * auc_score(labs, [s for s, _ in lst])
            gden += npos
        nd.append(ndcg_at_k(labs, k))
    gauc = float(gnum / gden) if gden else 0.5
    ndcg = float(sum(nd) / len(nd)) if nd else 0.0
    primary = (gauc + ndcg) / 2.0
    return {
        'GAUC': gauc,
        f'nDCG@{k}': ndcg,
        'primary': primary,
        'users': len(byu),
        'rows': len(labels)
    }
