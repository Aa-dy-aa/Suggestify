import os
import dotenv
from typing import List, Dict, Any
import pandas as pd

dotenv.load_dotenv()

# Try to import Anthropic client if available; otherwise provide a safe fallback
try:
    from anthropic import Anthropic  # type: ignore
except Exception:
    Anthropic = None  # type: ignore

CLAUDE_API_KEY = os.getenv("CLAUDE_API_KEY")


class RecommendationExplainer:
    """Generates short explanations for recommendations.

    If the Anthropic client and API key are available, it will attempt to call Claude.
    Otherwise it falls back to a deterministic explanation generator that uses
    product attributes (category, price, rating, similarity).
    """

    def __init__(self):
        self.client = None
        if Anthropic is not None and CLAUDE_API_KEY:
            try:
                self.client = Anthropic(api_key=CLAUDE_API_KEY)
            except Exception as e:
                # If client can't be initialized, continue with fallback
                print(f"Warning: could not initialize Anthropic client: {e}")

    def _llm_generate(self, prompt: str) -> str:
        """Call the Anthropic client to generate a short explanation. Returns empty string on failure."""
        if not self.client:
            return ""
        try:
            # Use safest call pattern: Anthropic client APIs vary; try to be defensive
            res = None
            # Newer Anthropic SDKs often provide .create_completion or .completion.create; try common patterns
            if hasattr(self.client, "completion"):
                res = self.client.completion.create(model="claude-2", prompt=prompt, max_tokens=120)
                text = res.get("completion") or res.get("text") or ""
            elif hasattr(self.client, "create"):
                res = self.client.create(prompt=prompt, max_tokens=120)
                text = getattr(res, "text", "") or res.get("text", "")
            else:
                # Last-resort: try messages API
                if hasattr(self.client, "messages") and hasattr(self.client.messages, "create"):
                    out = self.client.messages.create(model="claude-2", messages=[{"role": "user", "content": prompt}])
                    text = getattr(out, "content", "") or (out[0].get("text") if out else "")
                else:
                    text = ""

            if not text:
                return ""
            return str(text).strip()
        except Exception as e:
            print(f"Error calling Anthropic API: {e}")
            return ""

    def _simple_explanation(self, source_product: Dict[str, Any], recommended_product: Dict[str, Any]) -> str:
        parts: List[str] = []
        # category
        if source_product.get("category_name") and source_product.get("category_name") == recommended_product.get("category_name"):
            parts.append("from the same category")
        # price
        try:
            sp = float(source_product.get("price", 0) or 0)
            rp = float(recommended_product.get("price", 0) or 0)
            diff = abs(sp - rp)
            if diff < 10 and sp > 0:
                parts.append("a similar price")
            elif rp and rp < sp:
                parts.append("a more budget-friendly option")
            elif rp and rp > sp:
                parts.append("a premium alternative")
        except Exception:
            pass
        # rating
        try:
            if float(recommended_product.get("stars", 0) or 0) >= 4.0:
                parts.append("highly rated by customers")
        except Exception:
            pass
        # similarity
        try:
            sim = float(recommended_product.get("similarity_score", 0) or 0)
            if sim > 0.8:
                parts.append("very similar to your product")
            elif sim > 0.5:
                parts.append("shares several features with your product")
        except Exception:
            pass

        if not parts:
            return "This product shares features with items you viewed and could be of interest."

        # Construct concise explanation (max ~2 short clauses)
        explanation = " and ".join(parts[:3])
        return f"This product is {explanation}."

    def generate_explanation(self, source_product: Dict[str, Any], recommended_product: Dict[str, Any]) -> str:
        # Try LLM first if available
        try:
            prompt = f"Explain in 1-2 short sentences why someone who liked '{source_product.get('title','')}' might like '{recommended_product.get('title','')}'.\nContext:\nSource: {source_product}\nRecommended: {recommended_product}\nExplanation:"
            if self.client:
                out = self._llm_generate(prompt)
                if out:
                    return out.replace("\n", " ").strip()
        except Exception as e:
            print(f"LLM explanation failed: {e}")

        # Fallback deterministic explanation
        return self._simple_explanation(source_product, recommended_product)

    def batch_generate_explanations(self, source_product: Dict[str, Any], recommended_products: List[Dict[str, Any]]) -> List[str]:
        return [self.generate_explanation(source_product, rec) for rec in recommended_products]