from collections import Counter
from io import BytesIO

import matplotlib
import matplotlib.pyplot as plt

matplotlib.use("Agg")


def render_growth_time_histogram(freq: Counter[int]) -> bytes:
    """Render a bar chart of berry growth time frequencies as PNG bytes."""
    x = sorted(freq.keys())
    y = [freq[k] for k in x]

    fig, ax = plt.subplots()
    ax.bar([str(v) for v in x], y)
    ax.set_xlabel("Growth Time")
    ax.set_ylabel("Number of Berries")
    ax.set_title("Berry Growth Time Frequency")

    buf = BytesIO()
    fig.savefig(buf, format="png")
    plt.close(fig)
    buf.seek(0)

    return buf.getvalue()
