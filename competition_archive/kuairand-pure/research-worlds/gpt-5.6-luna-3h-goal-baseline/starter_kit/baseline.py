"""KuaiRand-Pure baselines。
  --model pop   : item popularity（官方 baseline，纯统计，不训练）
  --model fm    : Factorization Machine ranker（默认使用验证过的优化配置）
  --model random: 随机打分（下界，用来自检评测代码没坏）
只依赖 numpy。用法见 README.md
"""
import argparse, collections, time
import numpy as np
try:  # Support both ``python starter_kit/baseline.py`` and package imports.
    from .data import load, encode, FIELDS, RANKING_FIELDS, RICH_FIELDS
    from .evaluate import evaluate
except ImportError:
    from data import load, encode, FIELDS, RANKING_FIELDS, RICH_FIELDS
    from evaluate import evaluate

def sigmoid(x): return 1.0 / (1.0 + np.exp(-np.clip(x, -30, 30)))

# ---------------- item popularity（官方 baseline） ----------------
def run_pop(splits, prior=20.0):
    pos, imp = collections.Counter(), collections.Counter()
    for x in splits['train']:
        imp[x[2]] += 1; pos[x[2]] += x[6]
    gmean = sum(pos.values()) / sum(imp.values())
    score = lambda v: (pos[v] + prior * gmean) / (imp[v] + prior) if imp[v] else gmean
    out = {}
    for name in ('valid', 'test'):
        rws = splits[name]
        out[name] = evaluate([x[1] for x in rws], [x[6] for x in rws],
                             [score(x[2]) for x in rws])
    return out

def run_random(splits, seed=0):
    rng = np.random.default_rng(seed)
    out = {}
    for name in ('valid', 'test'):
        rws = splits[name]
        out[name] = evaluate([x[1] for x in rws], [x[6] for x in rws],
                             rng.random(len(rws)))
    return out

# ---------------- Factorization Machine ----------------
class FM:
    def __init__(self, dim, k=16, lr=0.001, l2=1e-6, seed=0, interaction_scales=None):
        rng = np.random.default_rng(seed)
        self.V = rng.normal(0, 0.01, (dim, k)).astype(np.float32)
        self.W = np.zeros(dim, dtype=np.float32)
        self.b = np.float32(0.0)
        self.lr, self.l2 = lr, l2
        self.interaction_scales = None if interaction_scales is None else np.asarray(interaction_scales, dtype=np.float32)
        self.mV = np.zeros_like(self.V); self.vV = np.zeros_like(self.V)
        self.mW = np.zeros_like(self.W); self.vW = np.zeros_like(self.W)
        self.t = 0

    def logits(self, X):
        E = self.V[X]                                   # (B,F,k)
        if self.interaction_scales is not None:
            E = E * self.interaction_scales[None, :, None]
        S = E.sum(1)                                    # (B,k)
        inter = 0.5 * ((S ** 2).sum(1) - (E ** 2).sum((1, 2)))
        return self.b + self.W[X].sum(1) + inter, E, S

    def step(self, X, y, weights=None):
        B = len(y)
        z, E, S = self.logits(X)
        if weights is None:
            weights = 1.0
        g = ((sigmoid(z) - y) * weights / B).astype(np.float32)  # (B,)
        gV = np.zeros_like(self.V); gW = np.zeros_like(self.W)
        np.add.at(gW, X, g[:, None])
        scale = 1.0 if self.interaction_scales is None else self.interaction_scales[None, :, None]
        np.add.at(gV, X, g[:, None, None] * (S[:, None, :] - E) * scale)
        gV += self.l2 * self.V; gW += self.l2 * self.W
        self.t += 1
        b1, b2, eps = 0.9, 0.999, 1e-8
        for P, G, M, Vv in ((self.V, gV, self.mV, self.vV), (self.W, gW, self.mW, self.vW)):
            M *= b1; M += (1 - b1) * G
            Vv *= b2; Vv += (1 - b2) * (G * G)
            P -= self.lr * (M / (1 - b1 ** self.t)) / (np.sqrt(Vv / (1 - b2 ** self.t)) + eps)
        self.b -= self.lr * g.sum()
        loss = y * np.log(sigmoid(z) + 1e-9) + (1 - y) * np.log(1 - sigmoid(z) + 1e-9)
        return float(-np.mean(weights * loss) if np.ndim(weights) else -np.mean(loss))

    def _apply_grad(self, gV, gW):
        """Apply one Adam update for gradients already averaged over a batch."""
        gV += self.l2 * self.V
        gW += self.l2 * self.W
        self.t += 1
        b1, b2, eps = 0.9, 0.999, 1e-8
        for P, G, M, Vv in ((self.V, gV, self.mV, self.vV), (self.W, gW, self.mW, self.vW)):
            M *= b1; M += (1 - b1) * G
            Vv *= b2; Vv += (1 - b2) * (G * G)
            P -= self.lr * (M / (1 - b1 ** self.t)) / (np.sqrt(Vv / (1 - b2 ** self.t)) + eps)

    def grad_step(self, X, grad):
        """Apply a supplied derivative with respect to each row's logit."""
        B = len(X)
        _, E, S = self.logits(X)
        grad = np.asarray(grad, dtype=np.float32)
        gV = np.zeros_like(self.V); gW = np.zeros_like(self.W)
        np.add.at(gW, X, grad[:, None])
        scale = 1.0 if self.interaction_scales is None else self.interaction_scales[None, :, None]
        np.add.at(gV, X, grad[:, None, None] * (S[:, None, :] - E) * scale)
        self._apply_grad(gV, gW)
        self.b -= self.lr * grad.sum()

    def pair_step(self, X_pos, X_neg):
        """One BPR step for positive/negative rows from the same users.

        The user field is intentionally present in both rows: its standalone
        term cancels, while its interactions with the candidate fields remain
        trainable.  This matches the within-user ranking objective.
        """
        B = len(X_pos)
        zp, Ep, Sp = self.logits(X_pos)
        zn, En, Sn = self.logits(X_neg)
        delta = zp - zn
        q = (sigmoid(-delta) / B).astype(np.float32)  # d softplus(-delta) / d z_pos
        gV = np.zeros_like(self.V); gW = np.zeros_like(self.W)
        np.add.at(gW, X_pos, q[:, None])
        np.add.at(gW, X_neg, -q[:, None])
        scale = 1.0 if self.interaction_scales is None else self.interaction_scales[None, :, None]
        np.add.at(gV, X_pos, q[:, None, None] * (Sp[:, None, :] - Ep) * scale)
        np.add.at(gV, X_neg, -q[:, None, None] * (Sn[:, None, :] - En) * scale)
        self._apply_grad(gV, gW)
        return float(np.mean(np.logaddexp(0.0, -delta)))

    def listwise_step(self, X, groups, labels):
        """Update on a per-user softmax target over mixed-label impressions."""
        z = self.logits(X)[0]
        grad = np.zeros(len(X), dtype=np.float32)
        active = 0
        loss = 0.0
        for inds in groups:
            y = labels[inds]
            npos = int(y.sum())
            if npos == 0 or npos == len(inds):
                continue
            zz = z[inds]
            zz = zz - np.max(zz)
            p = np.exp(zz)
            p /= p.sum()
            target = y / npos
            grad[inds] = p - target
            loss -= float(np.sum(target * np.log(p + 1e-9)))
            active += 1
        if active:
            self.grad_step(X, grad / active)
        return loss / active if active else 0.0

    def predict(self, X, bs=200_000):
        if len(X) == 0:
            return np.empty(0, dtype=np.float32)
        return np.concatenate([self.logits(X[i:i + bs])[0] for i in range(0, len(X), bs)])

def run_fm(splits, k=16, lr=0.001, epochs=40, bs=8192, patience=4, seed=0,
           verbose=True, fields=None, user_balance=0.0, positive_weight=2.0,
           recency_days=None, linear_only_fields=()):
    fields = RANKING_FIELDS if fields is None else list(fields)
    enc, dim = encode(splits, fields=fields)
    Xtr, ytr, utr = enc['train']; Xva, yva, uva = enc['valid']; Xte, yte, ute = enc['test']
    interaction_scales = [0.0 if field in linear_only_fields else 1.0 for field in fields]
    m = FM(dim, k=k, lr=lr, seed=seed, interaction_scales=interaction_scales)
    rng = np.random.default_rng(seed)
    row_weights = None
    if user_balance:
        counts = collections.Counter(utr)
        row_weights = np.asarray([counts[u] ** (-user_balance) for u in utr], dtype=np.float32)
    if positive_weight != 1.0:
        if row_weights is None:
            row_weights = np.ones(len(ytr), dtype=np.float32)
        row_weights *= np.where(ytr > 0.5, positive_weight, 1.0)
    if recency_days is not None:
        if row_weights is None:
            row_weights = np.ones(len(ytr), dtype=np.float32)
        train_end = max(x[0] for x in splits['train'])
        ages = np.asarray([train_end - x[0] for x in splits['train']], dtype=np.float32)
        row_weights *= np.exp(-ages / recency_days).astype(np.float32)
    if row_weights is not None:
        row_weights /= row_weights.mean()
    best, best_state, bad = -1, None, 0
    for ep in range(1, epochs + 1):
        idx = rng.permutation(len(ytr)); t0 = time.time()
        losses = [m.step(Xtr[idx[i:i + bs]], ytr[idx[i:i + bs]],
                         None if row_weights is None else row_weights[idx[i:i + bs]])
                  for i in range(0, len(idx), bs)]
        va = evaluate(uva, yva, m.predict(Xva))
        if verbose:
            print(f"  epoch {ep:2d} | loss {np.mean(losses):.4f} | valid GAUC {va['GAUC']:.4f} "
                  f"nDCG@5 {va['nDCG@5']:.4f} primary {va['primary']:.4f} | {time.time()-t0:.1f}s")
        if va['primary'] > best + 1e-5:
            best, bad = va['primary'], 0
            best_state = (m.V.copy(), m.W.copy(), np.float32(m.b))
        else:
            bad += 1
            if bad >= patience:
                if verbose: print(f"  early stop at epoch {ep}")
                break
    m.V, m.W, m.b = best_state
    return {'valid': evaluate(uva, yva, m.predict(Xva)),
            'test':  evaluate(ute, yte, m.predict(Xte))}


def _ranking_pairs(X, y, users, rng):
    """Sample one fresh negative for every positive within each training user."""
    by_user = collections.defaultdict(lambda: [[], []])
    for i, (u, label) in enumerate(zip(users, y)):
        by_user[u][int(label)].append(i)
    positives, negatives = [], []
    for pos, neg in by_user.values():
        if pos and neg:
            positives.extend(pos)
            negatives.extend(rng.choice(neg, size=len(pos), replace=True).tolist())
    if not positives:
        return np.empty((0, X.shape[1]), dtype=X.dtype), np.empty((0, X.shape[1]), dtype=X.dtype)
    order = rng.permutation(len(positives))
    return X[np.asarray(positives)[order]], X[np.asarray(negatives)[order]]


def run_pairwise(splits, k=16, lr=0.001, pair_lr=None, warmup_epochs=5, epochs=20,
                 bs=8192, patience=4, seed=0, verbose=True, fields=None):
    """FM with a pointwise warm start followed by within-user BPR updates."""
    enc, dim = encode(splits, fields=fields)
    Xtr, ytr, utr = enc['train']; Xva, yva, uva = enc['valid']; Xte, yte, ute = enc['test']
    m = FM(dim, k=k, lr=lr, seed=seed)
    rng = np.random.default_rng(seed)
    best, best_state, bad = -1, None, 0
    for ep in range(1, warmup_epochs + 1):
        idx = rng.permutation(len(ytr))
        for i in range(0, len(idx), bs):
            m.step(Xtr[idx[i:i + bs]], ytr[idx[i:i + bs]])
        va = evaluate(uva, yva, m.predict(Xva))
        if va['primary'] > best + 1e-5:
            best, bad = va['primary'], 0
            best_state = (m.V.copy(), m.W.copy(), np.float32(m.b), m.mV.copy(), m.vV.copy(), m.mW.copy(), m.vW.copy(), m.t)
        else:
            bad += 1
    if pair_lr is not None:
        m.lr = pair_lr
    for ep in range(1, epochs + 1):
        Xp, Xn = _ranking_pairs(Xtr, ytr, utr, rng)
        losses = []
        for i in range(0, len(Xp), bs):
            losses.append(m.pair_step(Xp[i:i + bs], Xn[i:i + bs]))
        va = evaluate(uva, yva, m.predict(Xva))
        if verbose:
            print(f"  pair epoch {ep:2d} | loss {np.mean(losses):.4f} | valid GAUC {va['GAUC']:.4f} "
                  f"nDCG@5 {va['nDCG@5']:.4f} primary {va['primary']:.4f}")
        if va['primary'] > best + 1e-5:
            best, bad = va['primary'], 0
            best_state = (m.V.copy(), m.W.copy(), np.float32(m.b), m.mV.copy(), m.vV.copy(), m.mW.copy(), m.vW.copy(), m.t)
        else:
            bad += 1
            if bad >= patience:
                break
    m.V, m.W, m.b, m.mV, m.vV, m.mW, m.vW, m.t = best_state
    return {'valid': evaluate(uva, yva, m.predict(Xva)),
            'test': evaluate(ute, yte, m.predict(Xte))}


def run_listwise(splits, k=16, lr=0.001, list_lr=None, warmup_epochs=5, epochs=10,
                 patience=4, seed=0, verbose=True, fields=None):
    """FM with a pointwise warm start followed by per-user softmax updates."""
    enc, dim = encode(splits, fields=fields)
    Xtr, ytr, utr = enc['train']; Xva, yva, uva = enc['valid']; Xte, yte, ute = enc['test']
    groups_by_user = collections.defaultdict(list)
    for i, u in enumerate(utr):
        groups_by_user[u].append(i)
    groups = [np.asarray(v, dtype=np.int32) for v in groups_by_user.values()]
    m = FM(dim, k=k, lr=lr, seed=seed)
    rng = np.random.default_rng(seed)
    best, best_state, bad = -1, None, 0
    bs = 8192
    for ep in range(1, warmup_epochs + 1):
        idx = rng.permutation(len(ytr))
        for i in range(0, len(idx), bs):
            m.step(Xtr[idx[i:i + bs]], ytr[idx[i:i + bs]])
        va = evaluate(uva, yva, m.predict(Xva))
        if va['primary'] > best + 1e-5:
            best, bad = va['primary'], 0
            best_state = (m.V.copy(), m.W.copy(), np.float32(m.b))
        else:
            bad += 1
    if list_lr is not None:
        m.lr = list_lr
    for ep in range(1, epochs + 1):
        loss = m.listwise_step(Xtr, groups, ytr)
        va = evaluate(uva, yva, m.predict(Xva))
        if verbose:
            print(f"  list epoch {ep:2d} | loss {loss:.4f} | valid GAUC {va['GAUC']:.4f} "
                  f"nDCG@5 {va['nDCG@5']:.4f} primary {va['primary']:.4f}")
        if va['primary'] > best + 1e-5:
            best, bad = va['primary'], 0
            best_state = (m.V.copy(), m.W.copy(), np.float32(m.b))
        else:
            bad += 1
            if bad >= patience:
                break
    m.V, m.W, m.b = best_state
    return {'valid': evaluate(uva, yva, m.predict(Xva)),
            'test': evaluate(ute, yte, m.predict(Xte))}

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--data_dir', default='./KuaiRand-Pure/data',
                    help='KuaiRand-Pure 解压后的 data 目录')
    ap.add_argument('--model', default='fm', choices=['pop', 'fm', 'pairwise', 'listwise', 'random'])
    ap.add_argument('--k', type=int, default=16)
    ap.add_argument('--lr', type=float, default=0.001)
    ap.add_argument('--epochs', type=int, default=40)
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--rich', action='store_true', help='use context and item-cross candidate fields')
    ap.add_argument('--official-control', action='store_true',
                    help='run the original 5-field, unweighted FM control')
    a = ap.parse_args()
    print(f"loading {a.data_dir} ...")
    splits = load(a.data_dir)
    fields = FIELDS if a.official_control else (RICH_FIELDS if a.rich else RANKING_FIELDS)
    positive_weight = 1.0 if a.official_control else 2.0
    print({k_: len(v) for k_, v in splits.items()}, f"fields={fields}, positive_weight={positive_weight}")
    res = {'pop': run_pop, 'random': lambda s: run_random(s, a.seed),
           'fm': lambda s: run_fm(s, k=a.k, lr=a.lr, epochs=a.epochs, seed=a.seed,
                                  fields=fields, positive_weight=positive_weight),
           'pairwise': lambda s: run_pairwise(s, k=a.k, lr=a.lr, epochs=a.epochs, seed=a.seed, fields=fields),
           'listwise': lambda s: run_listwise(s, k=a.k, lr=a.lr, epochs=a.epochs, seed=a.seed, fields=fields)}[a.model](splits)
    print(f"\n=== {a.model} (seed={a.seed}) ===")
    for sp in ('valid', 'test'):
        r = res[sp]
        print(f"  {sp:5s}  GAUC {r['GAUC']:.4f} | nDCG@5 {r['nDCG@5']:.4f} | primary {r['primary']:.4f}")
