"""KuaiRand-Pure 数据加载 + 官方划分 + 特征编码。只依赖标准库和 numpy。"""
import csv, os, collections
import numpy as np

LABEL = 'long_view'
SPLITS = {'train': (20220408, 20220421),
          'valid': (20220422, 20220428),
          'test':  (20220429, 20220508)}
# The five starter fields are kept as the reproducible official control.
FIELDS = ['user_id', 'video_id', 'author_id', 'tab', 'dur_bucket']
RANKING_FIELDS = FIELDS + ['tab_hour']

# Candidate fields used by the richer ranking experiments.  They are all
# derived from fields available before the impression is shown; no feedback
# columns are used here.
RICH_FIELDS = FIELDS + [
    'hour', 'date', 'video_type', 'upload_type', 'music_id', 'tag',
    'video_tab', 'video_hour', 'author_tab', 'author_hour',
    'user_tab', 'user_hour', 'tab_hour',
]

def load(data_dir):
    """读日志 + 视频侧特征，返回按划分切好的 dict。"""
    vidinfo = {}
    with open(os.path.join(data_dir, 'video_features_basic_pure.csv')) as fh:
        for r in csv.DictReader(fh):
            vidinfo[r['video_id']] = {
                'author_id': r['author_id'],
                'video_type': r['video_type'],
                'upload_type': r['upload_type'],
                'music_id': r['music_id'],
                'tag': r['tag'],
            }

    rows = []
    # Managed competition workspaces expose the training log and a separate
    # public-validation log.  The full archive uses the second standard-log
    # name instead.  Prefer the full name when it is available, but keep the
    # loader usable on the hidden-test-free public view.
    log_files = ['log_standard_4_08_to_4_21_pure.csv']
    evaluation_log = 'log_standard_4_22_to_5_08_pure.csv'
    public_log = 'log_public_4_22_to_4_28_pure.csv'
    if os.path.exists(os.path.join(data_dir, evaluation_log)):
        log_files.append(evaluation_log)
    elif os.path.exists(os.path.join(data_dir, public_log)):
        log_files.append(public_log)
    else:
        raise FileNotFoundError(
            f'expected {evaluation_log!r} or {public_log!r} in {data_dir!r}'
        )
    for f in log_files:
        with open(os.path.join(data_dir, f)) as fh:
            for r in csv.DictReader(fh):
                vi = vidinfo.get(r['video_id'], {})
                rows.append((int(r['date']), r['user_id'], r['video_id'],
                             vi.get('author_id', 'UNK'), r['tab'],
                             float(r['duration_ms']), 1 if r[LABEL] != '0' else 0,
                             r['hourmin'], r['time_ms'],
                             vi.get('video_type', 'UNK'), vi.get('upload_type', 'UNK'),
                             vi.get('music_id', 'UNK'), vi.get('tag', 'UNK'),
                             int(r['is_click'] != '0'), int(r['is_like'] != '0'),
                             int(r['is_follow'] != '0'), int(r['is_comment'] != '0'),
                             int(r['is_forward'] != '0'), int(r['is_hate'] != '0'),
                             float(r['play_time_ms']), float(r['profile_stay_time']),
                             float(r['comment_stay_time']), int(r['is_profile_enter'] != '0'),
                             int(r['is_rand'] != '0')))

    out = {}
    for name, (lo, hi) in SPLITS.items():
        out[name] = [x for x in rows if lo <= x[0] <= hi]
    return out

def _bucket_edges(durations, n=10):
    return np.quantile(np.asarray(durations), np.linspace(0, 1, n + 1)[1:-1])

def _field_value(x, field, edges):
    """Return one categorical value without looking at evaluation labels."""
    hour = str(int(x[7]) // 100) if len(x) > 7 else '0'
    duration_bucket = str(int(np.searchsorted(edges, x[5])))
    duration_5s = str(min(int(x[5] // 5000), 120))
    duration_log = str(int(np.log1p(max(x[5], 0.0)) * 2.0))
    video_type = x[9] if len(x) > 9 else 'UNK'
    upload_type = x[10] if len(x) > 10 else 'UNK'
    music_id = x[11] if len(x) > 11 else 'UNK'
    tag = x[12] if len(x) > 12 else 'UNK'
    values = {
        'user_id': x[1],
        'video_id': x[2],
        'author_id': x[3],
        'tab': x[4],
        'dur_bucket': duration_bucket,
        'dur_5s': duration_5s,
        'dur_log': duration_log,
        'hour': hour,
        'date': str(x[0]),
        'video_type': video_type,
        'upload_type': upload_type,
        'music_id': music_id,
        'tag': tag,
        'video_tab': f'{x[2]}|{x[4]}',
        'video_hour': f'{x[2]}|{hour}',
        'author_tab': f'{x[3]}|{x[4]}',
        'author_hour': f'{x[3]}|{hour}',
        'user_tab': f'{x[1]}|{x[4]}',
        'user_hour': f'{x[1]}|{hour}',
        'user_tag': f'{x[1]}|{tag}',
        'user_video_type': f'{x[1]}|{video_type}',
        'user_upload_type': f'{x[1]}|{upload_type}',
        'tab_hour': f'{x[4]}|{hour}',
        'tab_dur': f'{x[4]}|{duration_bucket}',
        'hour_dur': f'{hour}|{duration_bucket}',
        'tab_video_type': f'{x[4]}|{video_type}',
        'tab_upload_type': f'{x[4]}|{upload_type}',
        'tab_music': f'{x[4]}|{music_id}',
        'tab_tag': f'{x[4]}|{tag}',
    }
    try:
        return values[field]
    except KeyError:
        raise ValueError(f'unknown categorical field: {field}')


def encode(splits, fields=None, target_index=6):
    """把类别特征映射成连续 id。未见过的取值统一落到该域的 UNK 槽。
    返回 (X, y, users) per split，X 为 int32 (N, len(fields))，以及 field_dims。"""
    fields = FIELDS if fields is None else list(fields)
    tr = splits['train']
    edges = _bucket_edges([x[5] for x in tr])

    def raw(x):
        return [_field_value(x, field, edges) for field in fields]

    vocabs = [dict() for _ in fields]
    for x in tr:
        for i, v in enumerate(raw(x)):
            if v not in vocabs[i]:
                vocabs[i][v] = len(vocabs[i])
    unk = [len(v) for v in vocabs]                 # 每个域末尾留一个 UNK 槽
    field_dims = [len(v) + 1 for v in vocabs]
    offsets = np.cumsum([0] + field_dims[:-1]).astype(np.int32)

    enc = {}
    for name, rws in splits.items():
        X = np.empty((len(rws), len(fields)), dtype=np.int32)
        y = np.empty(len(rws), dtype=np.float32)
        users = []
        for n, x in enumerate(rws):
            for i, v in enumerate(raw(x)):
                X[n, i] = vocabs[i].get(v, unk[i]) + offsets[i]
            y[n] = x[target_index]
            users.append(x[1])
        enc[name] = (X, y, users)
    return enc, int(sum(field_dims))
