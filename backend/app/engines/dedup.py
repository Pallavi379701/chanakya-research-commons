import re
from typing import List, Dict, Any, Tuple, Set
from datasketch import MinHash, MinHashLSH

def tokenize(text: str) -> List[str]:
    """Tokenize and normalize text into words and word-bigrams for accurate semantic deduplication."""
    text = re.sub(r"[^\w\s]", " ", text.lower()).strip()
    words = [w for w in text.split() if len(w) > 2]
    if not words:
        return [text]
    bigrams = [f"{words[i]}_{words[i+1]}" for i in range(len(words)-1)]
    return words + bigrams

def compute_minhash(text: str, num_perm: int = 128) -> MinHash:
    """Generate MinHash signature for text."""
    m = MinHash(num_perm=num_perm)
    shingles = tokenize(text)
    for s in shingles:
        m.update(s.encode("utf-8"))
    return m

class DeduplicationEngine:
    def __init__(self, threshold: float = 0.65, num_perm: int = 128):
        self.threshold = threshold
        self.num_perm = num_perm
        self.lsh = MinHashLSH(threshold=threshold, num_perm=num_perm)
        self.signatures: Dict[int, MinHash] = {}
        self.titles: Dict[int, str] = {}

    def index_papers(self, papers: List[Any]):
        """Index papers into the LSH index."""
        self.lsh = MinHashLSH(threshold=self.threshold, num_perm=self.num_perm)
        self.signatures.clear()
        self.titles.clear()

        for p in papers:
            p_id = getattr(p, "id", None) or p.get("id") or p.get("paper_id")
            title = getattr(p, "title", None) or p.get("title", "")
            abstract = getattr(p, "abstract", None) or p.get("abstract", "")
            if not p_id or not title:
                continue
            
            combined_text = f"{title} {abstract[:120]}"
            sig = compute_minhash(combined_text, num_perm=self.num_perm)
            self.signatures[p_id] = sig
            self.titles[p_id] = combined_text
            try:
                self.lsh.insert(f"paper_{p_id}", sig)
            except ValueError:
                pass

    def find_duplicates_lsh(self) -> List[Tuple[int, int, float]]:
        """Find near-duplicate candidate pairs using LSH."""
        duplicate_pairs = []
        seen = set()

        for p_id, sig in self.signatures.items():
            results = self.lsh.query(sig)
            for res_str in results:
                other_id = int(res_str.replace("paper_", ""))
                if p_id != other_id:
                    pair_key = tuple(sorted((p_id, other_id)))
                    if pair_key not in seen:
                        seen.add(pair_key)
                        sim = sig.jaccard(self.signatures[other_id])
                        if sim >= self.threshold:
                            duplicate_pairs.append((pair_key[0], pair_key[1], sim))
        return duplicate_pairs

    def find_duplicates_baseline_exact(self) -> List[Tuple[int, int, float]]:
        """Exact normalized title matching baseline."""
        norm_map = {}
        duplicates = []
        for p_id, title in self.titles.items():
            norm = re.sub(r"[^\w\s]", "", title.lower()).strip()
            if norm in norm_map:
                duplicates.append((norm_map[norm], p_id, 1.0))
            else:
                norm_map[norm] = p_id
        return duplicates

    def deduplicate_search_results(self, papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Merge duplicates in search results: if the same paper appears across
        multiple sources, output it once with its combined source list.
        """
        if not papers:
            return []

        merged = []
        visited = set()
        
        # Build local minhash index for the search batch
        batch_lsh = MinHashLSH(threshold=0.6, num_perm=64)
        batch_sigs = {}
        
        for idx, p in enumerate(papers):
            sig = compute_minhash(p["title"], num_perm=64)
            batch_sigs[idx] = sig
            try:
                batch_lsh.insert(f"idx_{idx}", sig)
            except ValueError:
                pass

        for idx, p in enumerate(papers):
            if idx in visited:
                continue
            
            cluster = [idx]
            visited.add(idx)
            candidates = batch_lsh.query(batch_sigs[idx])
            
            for c_str in candidates:
                c_idx = int(c_str.replace("idx_", ""))
                if c_idx not in visited:
                    sim = batch_sigs[idx].jaccard(batch_sigs[c_idx])
                    if sim >= 0.6:
                        visited.add(c_idx)
                        cluster.append(c_idx)

            # Combine sources
            sources = set()
            for c_idx in cluster:
                src = papers[c_idx].get("source")
                if src:
                    sources.add(src)
                for s in papers[c_idx].get("sources", []):
                    sources.add(s)

            canonical = dict(papers[idx])
            canonical["sources"] = sorted(list(sources)) if sources else [papers[idx].get("source", "arXiv")]
            canonical["duplicate_cluster_size"] = len(cluster)
            merged.append(canonical)

        return merged

dedup_engine = DeduplicationEngine(threshold=0.5)
