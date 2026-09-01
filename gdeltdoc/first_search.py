from gdeltdoc import GdeltDoc, Filters

# keyword as a list = AND match (article must contain both words,
# not the exact phrase "Assam NGO")
f = Filters(keyword=["Assam", "NGO"], timespan="1d")

gd = GdeltDoc()
articles = gd.article_search(f)

print(articles.head())
print(f"\nTotal articles found: {len(articles)}")
