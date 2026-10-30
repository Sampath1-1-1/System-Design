# Extracted from manuscript/book1-traditional/29-distributed-data-processing.md §29.3.1 (listing 1). Edit the manuscript, not this file.
cat access.log | awk '{print $7}' | sort | uniq -c | sort -rn | head -5
