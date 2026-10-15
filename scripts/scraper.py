import json
import re
import asyncio
from playwright.async_api import async_playwright

# ALLE 13 TICKERS - Kopiëren en plakken!
TICKERS = ["ERIC", "TXRH", "QURE", "PAG", "IONS", "SMG", "QSR", "HRMY", "POST", "PTCT", "DECK", "TRU", "SAH"]

async def scrape_ticker(ticker):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            await page.goto(f"https://yrobot.us/chart/{ticker}", timeout=30000)
            await page.wait_for_timeout(5000)
            
            content = await page.inner_text("body")
            
            ai_match = re.search(r'AI\s*Score\s*[:\-]?\s*([\d\.]+)', content, re.IGNORECASE)
            sentiment_match = re.search(r'(\d{2,3})\s+(Bullish|Bearish|Neutral)', content, re.IGNORECASE)
            date_match = re.search(r'Analysis\s+([\d\/\s:]+)', content, re.IGNORECASE)
            
            return {
                "ticker": ticker,
                "aiScore": float(ai_match.group(1)) if ai_match else None,
                "analysisScore": int(sentiment_match.group(1)) if sentiment_match else None,
                "sentiment": sentiment_match.group(2) if sentiment_match else "Onbekend",
                "date": date_match.group(1).strip() if date_match else "N/A"
            }
        except Exception as e:
            print(f"Fout bij {ticker}: {e}")
            return {"ticker": ticker, "error": str(e)}
        finally:
            await browser.close()

async def main():
    results = []
    for ticker in TICKERS:
        print(f"Scrappen: {ticker}")
        data = await scrape_ticker(ticker)
        results.append(data)
        await asyncio.sleep(2)
    
    with open("data/data.json", "w") as f:
        json.dump(results, f, indent=2)
    print("✅ Data opgeslagen in data/data.json")

if __name__ == "__main__":
    asyncio.run(main())
