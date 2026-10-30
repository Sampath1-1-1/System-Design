# Extracted from manuscript/book1-traditional/01-what-is-system-design.md §1.3.2 (listing 1). Edit the manuscript, not this file.
"""Back-of-the-envelope estimator for the PhotoShare running example.

Uses SI units: 1 MB = 10**6 bytes, 1 TB = 10**12 bytes.
"""
from dataclasses import dataclass

SECONDS_PER_DAY = 86_400


@dataclass
class Workload:
    dau: int                  # daily active users
    views_per_user: float     # photo views per user per day
    uploads_per_user: float   # photo uploads per user per day
    stored_bytes_per_upload: int  # original + thumbnails, bytes
    served_bytes_per_view: int    # bytes sent to the client per view
    peak_factor: float = 3.0      # peak-hour rate / daily average rate


def estimate(w: Workload) -> dict:
    views_per_day = w.dau * w.views_per_user
    uploads_per_day = w.dau * w.uploads_per_user
    read_rps = views_per_day / SECONDS_PER_DAY
    write_rps = uploads_per_day / SECONDS_PER_DAY
    storage_per_day = uploads_per_day * w.stored_bytes_per_upload
    egress_bits_per_s = views_per_day * w.served_bytes_per_view * 8 / SECONDS_PER_DAY
    return {
        "read_rps_avg": read_rps,
        "read_rps_peak": read_rps * w.peak_factor,
        "write_rps_avg": write_rps,
        "write_rps_peak": write_rps * w.peak_factor,
        "storage_TB_per_day": storage_per_day / 1e12,
        "storage_PB_per_year": storage_per_day * 365 / 1e15,
        "egress_Gbps_avg": egress_bits_per_s / 1e9,
        "egress_Gbps_peak": egress_bits_per_s * w.peak_factor / 1e9,
    }


if __name__ == "__main__":
    for label, dau in [("v0 launch", 1_000), ("v3 scale", 10_000_000)]:
        w = Workload(dau=dau, views_per_user=50, uploads_per_user=0.2,
                     stored_bytes_per_upload=2_500_000,
                     served_bytes_per_view=200_000)
        print(label)
        for key, value in estimate(w).items():
            print(f"  {key:>20}: {value:,.3f}")
