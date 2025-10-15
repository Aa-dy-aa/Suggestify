import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from llm import RecommendationExplainer


class ContentBasedFiltering:
    def __init__(self, data_path=r'C:\Users\sundr\Desktop\Suggestify\dataset\amazon_products.csv'):
        """
        Initialize the content-based filtering recommender
        """
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.data = pd.read_csv(data_path)

        # Ensure 'imgUrl' exists
        if 'imgUrl' not in self.data.columns:
            self.data['imgUrl'] = "https://via.placeholder.com/300x200?text=No+Image"
        else:
            self.data['imgUrl'] = self.data['imgUrl'].fillna("https://via.placeholder.com/300x200?text=No+Image")

        self.prepare_content_features()
        self._create_tfidf_matrix()
        self.explainer = RecommendationExplainer()  # ✅ Initialize LLM explainer

    def prepare_content_features(self):
        """Combine relevant text fields for TF-IDF."""
        self.data = self.data.fillna('')
        self.data['content'] = self.data.apply(self._combine_features, axis=1)

    def _combine_features(self, row):
        """Combine product features into a single text string."""
        features = []

        # Weight title more heavily
        features.extend([str(row['title'])] * 3)

        if 'category_id' in self.data.columns:
            features.append(f"category_{str(row['category_id'])}")

        # Add price range
        if 'price' in self.data.columns:
            price = row['price']
            if pd.notna(price):
                if price < 100:
                    features.append("budget_price")
                elif price < 200:
                    features.append("mid_price")
                else:
                    features.append("premium_price")

        # Add rating and popularity
        if 'stars' in self.data.columns and pd.notna(row['stars']):
            features.append(f"rating_{int(row['stars'])}_stars")

        if 'isBestSeller' in self.data.columns and row['isBestSeller']:
            features.append("bestseller")

        if 'boughtInLastMonth' in self.data.columns and pd.notna(row['boughtInLastMonth']):
            bought = row['boughtInLastMonth']
            if bought > 1000:
                features.append("very_popular")
            elif bought > 500:
                features.append("popular")
            elif bought > 100:
                features.append("moderately_popular")

        return ' '.join(x for x in features if x and x.strip())

    def _create_tfidf_matrix(self):
        """Compute TF-IDF matrix for content similarity."""
        self.tfidf_matrix = self.vectorizer.fit_transform(self.data['content'])

    # ---------------------------------------------------------------
    # MAIN RECOMMENDATION LOGIC
    # ---------------------------------------------------------------
    def get_recommendations(self, asin, top_n=5):
        """
        Get top-N similar products with LLM explanations.
        Includes 'imgUrl' for each recommended product.
        """
        try:
            source_product = self.data[self.data['asin'] == asin].iloc[0].to_dict()
            item_idx = self.data.index[self.data['asin'] == asin].tolist()[0]

            # Compute cosine similarity
            cosine_sim = cosine_similarity(
                self.tfidf_matrix[item_idx:item_idx + 1],
                self.tfidf_matrix
            ).flatten()

            # Get top similar products (excluding the original)
            similar_indices = cosine_sim.argsort()[::-1][1:top_n + 1]

            # Build DataFrame
            columns = {
                'asin': self.data.iloc[similar_indices]['asin'].values,
                'title': self.data.iloc[similar_indices]['title'].values,
                'similarity_score': cosine_sim[similar_indices],
                'imgUrl': self.data.iloc[similar_indices]['imgUrl'].values  # ✅ Added imgUrl
            }

            optional_columns = ['description', 'category_id', 'category_name', 'price', 'stars', 'num_reviews']
            for col in optional_columns:
                if col in self.data.columns:
                    columns[col] = self.data.iloc[similar_indices][col].values

            recommendations = pd.DataFrame(columns)

            # ✅ Generate explanation using LLM (with fallback)
            explanations = []
            for _, rec in recommendations.iterrows():
                try:
                    # Use LLM to generate a human-readable reason
                    explanation = self.explainer.generate_explanation(
                        source_product, rec.to_dict()
                    )
                except Exception as e:
                    # Fallback rule-based reasoning
                    explanation = self._fallback_explanation(source_product, rec.to_dict())
                    print(f"LLM explanation failed: {e}")
                explanations.append(explanation)

            recommendations['explanation'] = explanations
            return recommendations

        except IndexError:
            print(f"Product with ASIN {asin} not found.")
            return None

    def _fallback_explanation(self, source_product, rec):
        """Simple backup explanation if LLM fails."""
        explanation = []
        if rec.get('category_name') == source_product.get('category_name'):
            explanation.append("it's from the same category")
        if rec.get('price') and source_product.get('price'):
            diff = abs(float(rec['price']) - float(source_product['price']))
            if diff < 10:
                explanation.append("has a similar price")
            elif rec['price'] < source_product['price']:
                explanation.append("is more budget-friendly")
            else:
                explanation.append("is a premium alternative")
        if rec.get('stars') and float(rec['stars']) >= 4:
            explanation.append("is highly rated by customers")
        return "This product " + " and ".join(explanation) + "."

    def get_recommendations_by_title(self, title, top_n=5):
        """Find a product by title and get recommendations."""
        match = self.data[self.data['title'].str.contains(title, case=False, na=False)]
        if match.empty:
            print(f"No products found for '{title}'.")
            return None
        return self.get_recommendations(match.iloc[0]['asin'], top_n)

    def get_similar_in_category(self, asin, top_n=5):
        """Recommend products from the same category."""
        try:
            idx = self.data.index[self.data['asin'] == asin].tolist()[0]
            cat_id = self.data.iloc[idx]['category_id']
            category_data = self.data[self.data['category_id'] == cat_id]

            if len(category_data) <= 1:
                return None

            cosine_sim = cosine_similarity(
                self.tfidf_matrix[idx:idx + 1],
                self.tfidf_matrix[category_data.index]
            ).flatten()

            similar_indices = cosine_sim.argsort()[::-1][1:top_n + 1]
            recs = category_data.iloc[similar_indices].copy()
            recs['similarity_score'] = cosine_sim[similar_indices]

            # ✅ Ensure imgUrl is included
            if 'imgUrl' not in recs.columns:
                recs['imgUrl'] = "https://via.placeholder.com/300x200?text=No+Image"

            return recs

        except IndexError:
            print(f"ASIN {asin} not found.")
            return None


if __name__ == "__main__":
    recommender = ContentBasedFiltering()
    first_item = recommender.data.iloc[0]
    print(f"Getting recommendations for: {first_item['title']}\n")
    recs = recommender.get_recommendations(first_item['asin'])
    print(recs[['title', 'similarity_score', 'explanation', 'imgUrl']].head())
