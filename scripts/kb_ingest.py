import argparse
from kb.ingest import ingest_paths, ingest_youtube, ingest_urls

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--user", default="global")
    ap.add_argument("--path", action="append")
    ap.add_argument("--url", action="append")
    ap.add_argument("--youtube", action="append")
    args = ap.parse_args()

    if args.path: ingest_paths(args.path, user=args.user)
    if args.url: ingest_urls(args.url, user=args.user)
    if args.youtube: ingest_youtube(args.youtube, user=args.user)
    print("Ingestion complete.")
