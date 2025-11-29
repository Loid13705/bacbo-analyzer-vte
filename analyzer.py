# analyzer.py
import sqlite3
import pandas as pd
from collections import defaultdict

class StatsAnalyzer:
    def __init__(self, db_file="bacbo_history.db"):
        self.db = db_file
        self.refresh()

    def refresh(self):
        conn = sqlite3.connect(self.db)
        self.df = pd.read_sql_query("SELECT id, ts, result FROM rounds ORDER BY id ASC", conn)
        conn.close()

    def last_n(self, n=10):
        if self.df.empty:
            return []
        return list(self.df['result'].tail(n))

    def compute_stats(self):
        if self.df.empty:
            return {"total":0}
        counts = self.df['result'].value_counts().to_dict()
        stats = {"total": len(self.df)}
        stats.update({k: int(v) for k,v in counts.items()})
        # runs summary
        runs = []
        cur = None
        length = 0
        for r in self.df['result']:
            if r == cur:
                length += 1
            else:
                if cur is not None:
                    runs.append((cur, length))
                cur = r
                length = 1
        if cur is not None:
            runs.append((cur, length))
        run_counts = defaultdict(list)
        for r,l in runs:
            run_counts[r].append(l)
        for k,v in run_counts.items():
            stats[f"{k}_max_run"] = max(v)
            stats[f"{k}_avg_run"] = round(sum(v)/len(v),2)
        return stats

    def check_run(self):
        if self.df.empty:
            return None
        seq = list(self.df['result'])
        last = seq[-1]
        length = 1
        for i in range(len(seq)-2, -1, -1):
            if seq[i] == last:
                length += 1
            else:
                break
        return {"result": last, "length": length}

    def to_dataframe(self):
        return self.df.copy()

    def summary_text(self):
        s = f"Total rounds: {len(self.df)}\n"
        counts = self.df['result'].value_counts().to_dict()
        s += "Counts: " + ", ".join(f"{k}:{v}" for k,v in counts.items())
        return s
