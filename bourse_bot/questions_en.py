"""Version 86 : « Vos questions » en anglais (en/questions.html), avec les mêmes réponses honnêtes adaptées à un public international.

Pas de conseil personnalisé, pas de promesse. Les règles fiscales françaises sont présentées comme telles. Liens vers les pages anglaises
du site quand elles existent, sinon vers la page française (signalée « in French »). Données structurées FAQPage, lien de langue avec
questions-bourse.html. Même accordéon animé que la version française.
"""
import html
import os
import re


def _e(s):
    return html.escape(str(s), quote=True)


MOTS = ("will the stock market crash, should I buy bitcoin now, how much does 100 a month grow, is investing risky, how to spot a trading scam, "
        "which stock will go up this week, can you predict a stock price tomorrow, is AI stock prediction reliable, free AI stock forecast, crypto that will explode, "
        "AI bubble crash, stock market today, crypto price prediction 2030, what does NYSE HKG EPA mean, are stock market forecasts reliable, "
        "will a stock that dropped recover, dollar cost averaging or lump sum, learn investing free, paper trading without real money")


def _cent(mensuel=100, taux=5, ans=20):
    t = taux / 100 / 12
    return mensuel * ((1 + t) ** (ans * 12) - 1) / t, mensuel * 12 * ans


def questions():
    total, verse = _cent()
    nb = lambda x: f"{x:,.0f}"
    return [
        ("crash", "Will the stock market crash?",
         "Nobody can know for sure, human or AI. What can be measured is <b>risk</b>: how much prices are expected to move, and how many stocks face a sharp drop. "
         "Our AI's one-month view is on <a href='stock-market-prediction.html'>stock market prediction</a>. Over long periods the big indices have so far recovered, "
         "but sometimes it took very long: more than 21 years for the CAC 40 (2000-2021) and more than 34 years for Japan's Nikkei (1989-2024)."),
        ("bitcoin", "Should I buy bitcoin now?",
         "We don't give personal advice: the answer depends on your situation. What you should know: bitcoin has lost more than 70% several times, only invest what you can afford to lose, "
         "and use a regulated platform. The AI's view, with its confidence level, is on <a href='crypto-prediction.html'>crypto prediction</a>; "
         "the <a href='stocks/btc-usd.html'>bitcoin page</a> shows its price range and past calls."),
        ("hundred", "How much does $100 a month grow in the stock market?",
         f"Nothing is guaranteed, but here is an order of magnitude. With 100 a month for 20 years and an average return of 5% a year (an assumption, not a promise), "
         f"you would have put in {nb(verse)} and end up with about <b>{nb(total)}</b>, before taxes and fees. A bad decade can give much less. "
         "Run your own numbers with the <a href='tools/compound-interest.html'>compound interest calculator</a>."),
        ("risky", "Is investing in stocks risky?",
         "Yes: the value of an investment can fall, sometimes a lot, and nothing is guaranteed. Risk is reduced by <b>diversifying</b> (a world index fund rather than one stock), "
         "investing over a <b>long</b> period, regularly, and keeping an emergency fund aside."),
        ("scam", "How do I spot a trading scam?",
         "Warning signs: a high <b>guaranteed</b> return, an offer \"valid today only\", contact through social media or messaging apps, huge leverage, a request to wire money abroad or in crypto. "
         "Always check the name on your financial regulator's warning list before doing anything (the SEC and FINRA in the US, the FCA in the UK, the AMF in France)."),
        ("this-week", "Which stock will go up this week?",
         "Nobody knows reliably: over a week, price moves are largely random. Radar Bourse's AI gives a <b>one-month</b> view with its chances and confidence, "
         "and publishes its misses on <a href='verified-calls.html'>verified calls</a>."),
        ("reliable-ai", "Is an AI stock predictor reliable?",
         "An AI can help, but none can read the future. On years it had never seen, Radar Bourse's AI got the direction right about 51 times out of 100 when its confidence "
         "was low and 58 times out of 100 when it was high. It is much better at forecasting how <b>agitated</b> a price will be. Be wary of any service that promises more without publishing its misses."),
        ("tomorrow", "Can you predict a stock price for tomorrow?",
         "Not reliably: over one day, noise dominates. So Radar Bourse doesn't forecast day by day; it gives a one-month view and a likely <b>price range</b>, free and without sign-up. "
         "Examples: <a href='stocks/nvda.html'>Nvidia</a>, <a href='stocks/tsla.html'>Tesla</a>, <a href='stocks/mc-pa.html'>LVMH</a>, <a href='stocks/air-pa.html'>Airbus</a>."),
        ("explode", "Which crypto will explode?",
         "Honest answer: nobody knows. Cryptos that \"exploded\" upwards often exploded downwards afterwards, and many small coins have disappeared. "
         "Compare the expected volatility of each crypto on <a href='crypto-prediction.html'>crypto prediction</a> instead."),
        ("dca", "Should I invest all at once or a little every month?",
         "In a rising market, investing all at once earns a bit more on average; investing monthly (dollar-cost averaging) avoids putting everything in at the worst moment and is easier to stick to. "
         "With small amounts, monthly investing is often the only realistic option, and that's fine."),
        ("recover", "Will a stock that has dropped a lot bounce back?",
         "Not necessarily. A big drop doesn't make a stock \"cheap\": it can reflect real problems (falling sales, debt, lawsuits), and some never recover. "
         "A 50% loss needs a 100% gain to get back to where you started. Before buying more, ask yourself whether you would buy it today at this price if you didn't already own it."),
        ("ai-bubble", "Is there an AI bubble and a risk of an AI crash?",
         "Nobody can time a crash. What we know: AI-related stocks have risen a lot and weigh heavily in the big US indices, so a disappointment would hit many portfolios. "
         "Past bubbles (the internet in 2000) made some technology indices lose more than 70%."),
        ("today", "What is the stock market doing today?",
         "The main indices, the day's biggest moves and the AI's view are on the <a href='index.html'>English home page</a> and in the <a href='../app-en.html'>live app</a>, "
         "updated automatically several times a day."),
        ("long-term", "Can anyone predict a crypto price for 2030 or 2050?",
         "No. Sites showing a precise price for XRP, Polkadot or Bitcoin in 2030 extend a trend or use an arbitrary formula, with no proof that it works. "
         "Over several years a crypto can rise tenfold or disappear. Radar Bourse only forecasts one month ahead and publishes its misses."),
        ("codes", "What do \"NYSE:\", \"HKG:\" or \"EPA:\" mean before a stock's name?",
         "It's the code of the exchange where the stock is listed, followed by its ticker: NYSE and NASDAQ for New York, LON for London, EPA for Euronext Paris (EPA: MC = LVMH), "
         "HKG for Hong Kong, TPE for Taiwan, TYO for Tokyo. One company can be listed on several exchanges, in different currencies. Browse them all on "
         "<a href='all-stocks.html'>all stocks</a>."),
        ("forecasts-reliable", "Are stock market forecasts reliable?",
         "On short-term direction, no forecast is very reliable: even the best models are right a little more than half the time. Volatility (how much a price may move) "
         "is forecast far better than direction. A serious forecast gives a probability, a range and its past results, misses included, like our <a href='verified-calls.html'>verified calls</a>."),
        ("tax-france", "How are investment gains taxed in France in 2026?",
         "For French tax residents, gains and dividends on an ordinary securities account (and crypto gains) are taxed at a flat <b>31.4%</b> in 2026 (12.8% income tax + 18.6% social charges). "
         "A PEA held more than 5 years only pays social charges on gains. Other countries have very different rules: check your own tax authority. "
         "Calculator: <a href='tools/capital-gains.html'>capital gains</a>."),
        ("learn", "Where can I learn investing for free?",
         "The Radar Bourse Academy is free and needs no account: short lessons with corrected exercises, case studies and a final exam with a certificate "
         "(<a href='../formation.html'>in French</a>). In English, start with the <a href='guides.html'>beginner guides</a>."),
        ("practice", "Where can I practise without real money?",
         "In the <a href='../app-en.html'>app</a>: a virtual portfolio and a daily forecast game against the AI, free and without sign-up."),
    ]


def generer(base, dossier, csp=""):
    from . import anglais, seo
    qs = questions()
    blocs = "".join(f"<details class='q-bloc' id='{a}'><summary><h2>{_e(q)}</h2><span class='q-plus' aria-hidden='true'></span></summary>"
                    f"<div class='q-rep'><p>{r}</p></div></details>" for a, q, r in qs)
    sommaire = "".join(f"<li><a href='#{a}'>{_e(q)}</a></li>" for a, q, _ in qs)
    from .questions import CSS_ACCORDEON, JS_ACCORDEON
    corps = (CSS_ACCORDEON + "<h1>Your questions about stocks, crypto and AI</h1>"
             "<p class='muted'>The questions people ask most, with honest answers: when nobody can know, we say so. This is not personal financial advice. <a href='../questions-bourse.html' hreflang='fr' lang='fr'>Version française</a></p>"
             f"<ol class='q-sommaire'>{sommaire}</ol><p class='q-outils'><button class='btn ghost' type='button' id='q-tout' data-ouvrir='Open all' data-fermer='Close all'>Open all</button></p>"
             f"{blocs}{JS_ACCORDEON}")
    chemin = "en/questions.html"
    alt = {"fr": "questions-bourse.html", "en": chemin, "x-default": "questions-bourse.html"}
    page = anglais._page(base, "Stock market and AI questions: honest answers | Radar Bourse",
                         "Will the market crash? Should I buy bitcoin? How much does $100 a month grow? Is an AI stock predictor reliable? Honest, numbers-based answers.",
                         chemin, corps, csp, alt, mots=MOTS)
    jl = {"@context": "https://schema.org", "@type": "FAQPage", "inLanguage": "en", "mainEntity": [
        {"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": re.sub(r"<[^>]+>", "", r)}} for _a, q, r in qs]}
    import json
    page = page.replace("</head>", f"<script type=\"application/ld+json\">{json.dumps(jl, ensure_ascii=False)}</script>\n</head>", 1)
    os.makedirs(os.path.join(dossier, "en"), exist_ok=True)
    with open(os.path.join(dossier, chemin), "w", encoding="utf-8") as f:
        f.write(page)
    return [chemin]
