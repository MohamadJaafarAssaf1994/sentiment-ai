#   def legacy_predict(text):
#     if text == "":
#         return "NEGATIVE"
#     return "POSITIVE"
class SentimentModel:
    def __init__(self):
        print("[SentimentModel] Modele charge")

    def predict(self, text: str) -> dict:
        text_lower = text.lower()

        positive_words = [
            "bien", "super", "excellent", "parfait", "bon", "aime", "adore"
        ]
        negative_words = [
            "mal", "nul", "horrible", "mauvais", "deteste", "pire"
        ]

        pos = sum(1 for w in positive_words if w in text_lower)
        neg = sum(1 for w in negative_words if w in text_lower)

        if pos > neg:
            return {
                "label": "POSITIVE",
                "score": min(round(0.6 + 0.1 * pos, 2), 1.0),
                "text": text,
            }

        if neg > pos:
            return {
                "label": "NEGATIVE",
                "score": min(round(0.6 + 0.1 * neg, 2), 1.0),
                "text": text,
            }

        return {
            "label": "NEUTRAL",
            "score": 0.5,
            "text": text,
        }
