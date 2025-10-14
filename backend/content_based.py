import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from llm import RecommendationExplainer


class ContentBasedFiltering:
    def __init__(self, data_path=r'D:\LLM-based-Recommendation\dataset\amazon_products.csv'):
        """
        Initialize the content-based filtering recommender
        
        Parameters:
        -----------
        data_path : str
            Path to the Amazon products dataset CSV file
        """
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.data = pd.read_csv(data_path)
        self.prepare_content_features()
        self.tfidf_matrix = None
        self._create_tfidf_matrix()
        self.explainer = RecommendationExplainer()

    def prepare_content_features(self):
        """Prepare content features by combining relevant columns"""
        # Clean the data by filling NaN values
        self.data = self.data.fillna('')
        
        # Create the content column
        self.data['content'] = self.data.apply(self._combine_features, axis=1)
        
    def _combine_features(self, row):
        """
        Combine relevant features into a single text string
        
        This function combines various product features into a single text for TF-IDF processing
        """
        features = []
        
        # Add title with higher weight (3x)
        features.extend([str(row['title'])] * 3)
        
        # Add category_id as text
        if 'category_id' in self.data.columns:
            features.append(f"category_{str(row['category_id'])}")
        
        # Add price range information
        if 'price' in self.data.columns:
            price = row['price']
            if pd.notna(price):
                if price < 100:
                    features.append("budget_price")
                elif price < 200:
                    features.append("mid_price")
                else:
                    features.append("premium_price")
        
        # Add rating information
        if 'stars' in self.data.columns:
            stars = row['stars']
            if pd.notna(stars):
                features.append(f"rating_{int(stars)}_stars")
        
        # Add bestseller status
        if 'isBestSeller' in self.data.columns:
            if row['isBestSeller']:
                features.append("bestseller")
                
        # Add popularity information
        if 'boughtInLastMonth' in self.data.columns:
            bought = row['boughtInLastMonth']
            if pd.notna(bought):
                if bought > 1000:
                    features.append("very_popular")
                elif bought > 500:
                    features.append("popular")
                elif bought > 100:
                    features.append("moderately_popular")
        
        # Clean and join all features (remove empty strings and strip whitespace)
        return ' '.join(x for x in features if x and x.strip())

    def _create_tfidf_matrix(self):
        """Create TF-IDF matrix from the content features"""
        self.tfidf_matrix = self.vectorizer.fit_transform(self.data['content'])
        
    def get_recommendations(self, asin, top_n=5):
        """
        Get top N recommendations for a given product ASIN with explanations
        
        Parameters:
        -----------
        asin : str
            The ASIN (Amazon Standard Identification Number) of the product
        top_n : int, optional (default=5)
            Number of recommendations to return
            
        Returns:
        --------
        DataFrame containing recommended items with their similarity scores and explanations
        """
        try:
            # Get source product data
            source_product = self.data[self.data['asin'] == asin].iloc[0].to_dict()
            item_idx = self.data.index[self.data['asin'] == asin].tolist()[0]
            
            # Calculate cosine similarity between this item and all others
            cosine_sim = cosine_similarity(self.tfidf_matrix[item_idx:item_idx+1], self.tfidf_matrix).flatten()
            
            # Get indices of top N similar items (excluding the item itself)
            similar_indices = cosine_sim.argsort()[::-1][1:top_n+1]
            
            # Create base recommendations dataframe with available columns
            columns = {
                'asin': self.data.iloc[similar_indices]['asin'].values,
                'title': self.data.iloc[similar_indices]['title'].values,
                'similarity_score': cosine_sim[similar_indices]
            }
            
            # Add optional columns if they exist in the dataset
            optional_columns = ['description', 'category_id', 'category_name', 'price', 'stars', 'num_reviews']
            for col in optional_columns:
                if col in self.data.columns:
                    columns[col] = self.data.iloc[similar_indices][col].values
            
            recommendations = pd.DataFrame(columns)
            
            # Generate simple explanations based on similarities
            explanations = []
            for _, rec in recommendations.iterrows():
                explanation = []
                
                # Check category similarity
                if 'category_name' in recommendations.columns and rec['category_name'] == source_product.get('category_name'):
                    explanation.append("it's from the same category")
                
                # Compare price
                if 'price' in recommendations.columns:
                    price_diff = abs(float(rec.get('price', 0)) - float(source_product.get('price', 0)))
                    if price_diff < 10:
                        explanation.append("has a similar price point")
                    elif rec.get('price', 0) < source_product.get('price', 0):
                        explanation.append("offers a more budget-friendly option")
                    else:
                        explanation.append("is a premium alternative")
                
                # Compare ratings
                if 'stars' in recommendations.columns:
                    if float(rec.get('stars', 0)) >= 4.0:
                        explanation.append("is highly rated by customers")
                
                # Add similarity context
                if rec['similarity_score'] > 0.8:
                    explanation.append("is very similar to your selected product")
                elif rec['similarity_score'] > 0.5:
                    explanation.append("shares several features with your selection")
                
                final_explanation = "This product " + " and ".join(explanation) + "."
                explanations.append(final_explanation)
            
            recommendations['explanation'] = explanations
            
            return recommendations
            
        except IndexError:
            print(f"Product with ID {product_id} not found in the dataset.")
            return None
    
    def get_recommendations_by_title(self, title, top_n=5):
        """
        Get recommendations by product title
        
        Parameters:
        -----------
        title : str
            Full or partial title of the product
        top_n : int, optional (default=5)
            Number of recommendations to return
            
        Returns:
        --------
        DataFrame containing recommended items with their similarity scores
        """
        # Find products matching the title
        matching_products = self.data[self.data['title'].str.contains(title, case=False, na=False)]
        
        if matching_products.empty:
            print(f"No products found matching '{title}'")
            return None
            
        # Get recommendations for the first matching product
        return self.get_recommendations(matching_products.iloc[0]['asin'], top_n)

    def get_similar_in_category(self, asin, top_n=5):
        """
        Get recommendations for products in the same category
        
        Parameters:
        -----------
        asin : str
            The ASIN of the product
        top_n : int, optional (default=5)
            Number of recommendations to return
            
        Returns:
        --------
        DataFrame containing recommended items from the same category
        """
        try:
            # Get the product's category
            product_idx = self.data.index[self.data['asin'] == asin].tolist()[0]
            product_category = self.data.iloc[product_idx]['category_id']
            
            # Filter data for the same category
            # Filter data for the same category
            category_data = self.data[self.data['category_id'] == product_category]
            
            if len(category_data) <= 1:
                print(f"Not enough products in category {product_category} for recommendations")
                return None
            
            # Calculate similarities for products in the same category
            cosine_sim = cosine_similarity(
                self.tfidf_matrix[product_idx:product_idx+1], 
                self.tfidf_matrix[category_data.index]
            ).flatten()
            
            # Get top N similar items (excluding the item itself)
            similar_indices = cosine_sim.argsort()[::-1][1:top_n+1]
            
            # Create base recommendations dataframe
            base_columns = {
                'asin': category_data.iloc[similar_indices]['asin'].values,
                'title': category_data.iloc[similar_indices]['title'].values,
                'similarity_score': cosine_sim[similar_indices],
                'price': category_data.iloc[similar_indices]['price'].values,
                'stars': category_data.iloc[similar_indices]['stars'].values
            }
            
            # Add optional columns if they exist
            optional_columns = {
                'category_id': 'category_id',
                'isBestSeller': 'isBestSeller',
                'boughtInLastMonth': 'boughtInLastMonth',
                'listPrice': 'listPrice'
            }
            
            for col, source_col in optional_columns.items():
                if source_col in category_data.columns:
                    base_columns[col] = category_data.iloc[similar_indices][source_col].values
            
            recommendations = pd.DataFrame(base_columns)
            return recommendations
            
        except IndexError:
            print(f"Product with ASIN {asin} not found in the dataset.")
            return None
        """
        Get recommendations for a product by its title
        
        Parameters:
        -----------
        product_title : str
            Title or partial title of the product
        top_n : int, optional (default=5)
            Number of recommendations to return
            
        Returns:
        --------
        DataFrame containing recommended items with their similarity scores
        """
        # Find products matching the title
        matching_products = self.data[self.data['product_title'].str.contains(product_title, case=False, na=False)]
        
        if matching_products.empty:
            print(f"No products found matching '{product_title}'")
            return None
            
        # Get recommendations for the first matching product
        return self.get_recommendations(matching_products.iloc[0]['asin'], top_n)

if __name__ == "__main__":
    # Initialize recommender
    recommender = ContentBasedFiltering()
    
    try:
        # Example: Get recommendations for the first item
        first_item = recommender.data.iloc[0]
        print(f"\nGetting recommendations for: {first_item['title']}")
        
        # Get general recommendations
        print("\nTop 5 Similar Products:")
        recommendations = recommender.get_recommendations(first_item['asin'])
        if recommendations is not None:
            display_cols = ['title', 'similarity_score', 'stars', 'price']
            display_cols = [col for col in display_cols if col in recommendations.columns]
            print(recommendations[display_cols].to_string(index=False))
        
        # Get category-specific recommendations
        print("\nTop 5 Similar Products in Same Category:")
        category_recommendations = recommender.get_similar_in_category(first_item['asin'])
        if category_recommendations is not None:
            display_cols = ['title', 'similarity_score', 'stars', 'price']
            display_cols = [col for col in display_cols if col in category_recommendations.columns]
            print(category_recommendations[display_cols].to_string(index=False))
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")