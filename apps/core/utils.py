"""
Car Delights Pricing & Formatting Utilities
"""

def format_inr(amount):
    """
    Format numeric values into the standard Indian numbering currency format (₹).
    e.g.:
      1500000 -> ₹15,00,000
      2015000 -> ₹20,15,000
      849000  -> ₹8,49,000
      585000  -> ₹5,85,000
      122500000 -> ₹12,25,00,000
      9500    -> ₹9,500
      450     -> ₹450
    """
    if amount is None:
        return "₹0"
    try:
        val = int(round(float(amount)))
    except (ValueError, TypeError):
        return f"₹{amount}"

    is_negative = val < 0
    s = str(abs(val))
    if len(s) <= 3:
        formatted = s
    else:
        last3 = s[-3:]
        remaining = s[:-3]
        parts = []
        while len(remaining) > 2:
            parts.insert(0, remaining[-2:])
            remaining = remaining[:-2]
        if remaining:
            parts.insert(0, remaining)
        formatted = f"{','.join(parts)},{last3}"

    return f"-₹{formatted}" if is_negative else f"₹{formatted}"
