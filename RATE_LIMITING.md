# Rate Limiting & Error Handling

## Problem Solved

When using Replicate with less than $5 in credit, the API has strict rate limits:
- **6 requests per minute** with a burst of 1 request
- This caused panels 2-5 to fail with 429 (Rate Limited) errors
- Images were generated too quickly without respecting rate limits

## Solution Implemented

### 1. Rate Limiting

**Automatic delays between requests:**
- Minimum 10 seconds between each image generation request
- Calculated as: 60 seconds / 6 requests = 10 seconds per request
- Prevents hitting rate limits proactively

### 2. Retry Logic with Exponential Backoff

**When rate limited (429 error):**
- Automatically retries up to 3 times
- Exponential backoff: 5s, 10s, 20s delays
- Shows progress messages during retries

**Error handling:**
- Catches `ReplicateError` specifically
- Handles 429 (rate limit) vs other API errors
- Provides user-friendly error messages

### 3. Better Error Messages

**Placeholder images now show:**
- Specific error type (rate limit, API error, etc.)
- Truncated error messages for readability
- Panel number for context

### 4. Progress Feedback

**UI shows:**
- Rate limiting status messages
- Retry attempts in progress
- Time estimates for generation

## How It Works

```
Request 1 → Generate → Wait 10s → Request 2 → Generate → Wait 10s → ...
         ↓
    If 429 error:
         ↓
    Wait 5s → Retry → If fails → Wait 10s → Retry → If fails → Wait 20s → Retry
         ↓
    If all retries fail → Show placeholder with error message
```

## Rate Limit Details

**Replicate Free Tier (<$5 credit):**
- 6 requests per minute
- Burst: 1 request
- Our delay: 10 seconds (safe margin)

**Replicate Paid Tier (>$5 credit):**
- Higher rate limits
- Our code still works (just waits less if needed)

## Impact on Generation Time

**Before (no rate limiting):**
- All requests sent immediately
- First succeeds, rest fail with 429
- Result: Only 1 panel generated

**After (with rate limiting):**
- 10 seconds between each panel
- For 4 panels: ~40 seconds additional wait time
- For 2 character references: ~20 seconds additional wait time
- **Total additional time: ~60 seconds for a 4-panel comic**
- **Result: All panels generate successfully**

## Code Changes

### ImageGenerator
- Added `min_delay_between_requests = 10` seconds
- Added `_wait_for_rate_limit()` method
- Added retry loop with exponential backoff
- Improved error handling

### CharacterGenerator
- Same rate limiting and retry logic
- Ensures character reference images also respect limits

## User Experience

**What users see:**
1. "Rate limiting: waiting X seconds..." messages
2. "Rate limited. Waiting X seconds before retry..." if errors occur
3. Progress continues even if some images take longer
4. Clear error messages if generation fails

**Benefits:**
- All panels generate successfully
- No more placeholder images due to rate limits
- Transparent about wait times
- Automatic retry on temporary failures

## Troubleshooting

### Still getting rate limit errors?

1. **Check your Replicate account balance:**
   - Go to https://replicate.com/account
   - If <$5, you're on free tier with strict limits

2. **Increase delay (if needed):**
   - Edit `min_delay_between_requests` in code
   - Default: 10 seconds (safe for 6 req/min)

3. **Add more credit:**
   - Adding $5+ increases rate limits significantly
   - Reduces wait times

### Generation taking too long?

- This is expected with free tier rate limits
- Each panel takes 10-30 seconds (generation + rate limit delay)
- 4 panels = ~40-120 seconds total
- Consider upgrading Replicate account for faster generation

## Future Improvements

- Dynamic rate limit detection from API response headers
- Adaptive delays based on account tier
- Queue system for batch generation
- Parallel generation for paid tier accounts

