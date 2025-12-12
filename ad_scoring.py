# ad_scoring.py
# Simple ad scoring example: score ads by CTR and bid with a little weighting.

def score(ad):
    """
    ad: dict with keys:
      - ctr (float) click-through rate (0..1)
      - bid (float) bid amount in USD
      - quality (float) 0..1 quality score (optional)
    returns float score (higher is better)
    """
    ctr = float(ad.get("ctr", 0.0))
    bid = float(ad.get("bid", 0.0))
    quality = float(ad.get("quality", 0.5))

    # basic scoring formula
    # multiply ctr by a factor and combine with normalized bid and quality
    score_val = (ctr * 100.0) * 0.6 + (bid * 10.0) * 0.3 + (quality * 100.0) * 0.1
    return score_val
