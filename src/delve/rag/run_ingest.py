from delve.rag.ingest import ingest_postmortems

count = ingest_postmortems()
print(f"Ingested {count} postmortems into Chroma")
