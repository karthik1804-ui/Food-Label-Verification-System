import os
import re
import docx

def analyze_report_text():
    doc_path = r"d:\food-risk-checker\final_report\MCA_Project_Report.docx"
    doc = docx.Document(doc_path)
    
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    
    print(f"Total Paragraphs: {len(paragraphs)}")
    
    # 1. AI Cliche Search
    ai_cliches = [
        "delve", "testament", "pivotal", "harness", "multifaceted", "plethora",
        "paramount", "beacon", "synergy", "seamlessly", "in today's", "it is important to note",
        "in conclusion", "furthermore", "moreover", "notably", "it is worth noting",
        "crucial role", "revolutioniz", "tapestry", "ever-evolving", "landscape"
    ]
    
    cliche_counts = {c: 0 for c in ai_cliches}
    cliche_matches = []
    
    for i, p in enumerate(paragraphs):
        p_lower = p.lower()
        for c in ai_cliches:
            if c in p_lower:
                cliche_counts[c] += 1
                cliche_matches.append((i, c, p[:80]))
                
    print("\n--- AI Cliche Frequencies ---")
    for c, count in sorted(cliche_counts.items(), key=lambda x: x[1], reverse=True):
        if count > 0:
            print(f"  {c}: {count} occurrences")
            
    # 2. Duplicate or Near-Duplicate Sentences
    sentence_counts = {}
    for i, p in enumerate(paragraphs):
        sentences = re.split(r'(?<=[.!?])\s+', p)
        for s in sentences:
            s_clean = s.strip()
            if len(s_clean.split()) > 7: # significant sentence
                sentence_counts[s_clean] = sentence_counts.get(s_clean, []) + [i]
                
    duplicates = {s: idxs for s, idxs in sentence_counts.items() if len(idxs) > 1}
    print(f"\n--- Repeated Sentences (count: {len(duplicates)}) ---")
    for s, idxs in list(duplicates.items())[:10]:
        print(f"  Repeated in paragraphs {idxs}: \"{s[:80]}...\"")
        
    # 3. Citation Analysis
    citations_in_text = []
    for i, p in enumerate(paragraphs):
        matches = re.findall(r'\[(\d+)\]', p)
        for m in matches:
            citations_in_text.append((int(m), i))
            
    unique_cited = set(c[0] for c in citations_in_text)
    print(f"\n--- In-Text Citation Analysis ---")
    print(f"Total citation callouts: {len(citations_in_text)}")
    print(f"Distinct reference IDs cited: {sorted(list(unique_cited))}")
    
    # Check which of the 38 references are cited
    uncited = [r for r in range(1, 39) if r not in unique_cited]
    print(f"References (1-38) NOT cited in text: {uncited}")
    
    # Check for citation IDs > 38
    invalid_citations = [c for c in unique_cited if c > 38 or c < 1]
    print(f"Citation IDs outside [1-38]: {invalid_citations}")

if __name__ == "__main__":
    analyze_report_text()
