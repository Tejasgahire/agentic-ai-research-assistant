import time
from google.genai import errors


def call_with_retry(func, *args, max_retries: int = 5, default_wait: int = 20, **kwargs):
    """
    Calls func(*args, **kwargs) and automatically retries on Gemini 429
    (rate limit / quota exceeded) errors, waiting between attempts.
    """
    for attempt in range(1, max_retries + 1):
        try:
            return func(*args, **kwargs)
        except errors.ClientError as e:
            is_rate_limit = getattr(e, "code", None) == 429 or "RESOURCE_EXHAUSTED" in str(e)
            if not is_rate_limit or attempt == max_retries:
                raise

            wait_time = default_wait
            print(f"Rate limit hit. Waiting {wait_time}s before retry "
                  f"(attempt {attempt}/{max_retries})...")
            time.sleep(wait_time)

    raise RuntimeError("call_with_retry: exhausted retries without success")