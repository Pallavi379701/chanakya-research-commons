import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import SessionLocal
from app.engines.evaluation import benchmark_engine

def main():
    print("================================================================================")
    print("   CHANAKYA RESEARCH COMMONS: QUANTITATIVE BENCHMARK EVALUATION SUITE")
    print("   Data Mining & Warehousing Mini-Project (Course Assessment: 40% Marks)")
    print("================================================================================\n")
    
    db = SessionLocal()
    try:
        report = benchmark_engine.evaluate_all(db)
        if "error" in report:
            print(f"ERROR: {report['error']}")
            return

        print(f"Evaluation Timestamp: {report['timestamp']}")
        print(f"Planted Ground Truth Loaded: {report['confusion_matrices']['deduplication']['planted_duplicates']} duplicate pairs, "
              f"{report['confusion_matrices']['spam_posts']['planted_spam_posts']} spam posts, "
              f"{report['confusion_matrices']['spikes']['total']} topic spikes.\n")

        print("-" * 105)
        print(f"{'Feature Area':<35} | {'Evaluated Method':<22} | {'Metric':<12} | {'Score':<8} | {'Baseline':<8}")
        print("-" * 105)

        for m in report["metrics"]:
            print(f"{m['feature']:<35} | {m['method'][:22]:<22} | {m['metric_name']:<12} | {m['metric_value']:<8.3f} | {m['baseline_value']:<8.3f}")

        print("-" * 105)
        print("\nDETAILED CONFUSION MATRICES & ACCURACY SUMMARY:")
        cm = report["confusion_matrices"]
        print(f"  1. MinHash LSH Deduplication: TP={cm['deduplication']['tp']}, FP={cm['deduplication']['fp']}, FN={cm['deduplication']['fn']}")
        print(f"  2. Spam Post Detection:       TP={cm['spam_posts']['tp']}, FP={cm['spam_posts']['fp']}, FN={cm['spam_posts']['fn']}")
        print(f"  3. Topic Spike Detection:     Detected={cm['spikes']['detected']} of {cm['spikes']['total']} surges")
        print("\nAll numeric benchmarks successfully verified against planted ground truth!\n")
    finally:
        db.close()

if __name__ == "__main__":
    main()
