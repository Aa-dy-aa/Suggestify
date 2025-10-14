from content_based import ContentBasedFiltering
import pandas as pd
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)

def test_recommendations():
    try:
        # Initialize the recommender
        print("Initializing recommender system...")
        recommender = ContentBasedFiltering()
        
        # Let's get a sample product ASIN from the dataset
        sample_product = recommender.data.iloc[0]
        print("\nSource Product:")
        print(f"ASIN: {sample_product['asin']}")
        print(f"Title: {sample_product['title']}")
        print(f"Category: {sample_product.get('category_name', 'N/A')}")
        print(f"Price: ${sample_product.get('price', 'N/A')}")
        print(f"Rating: {sample_product.get('stars', 'N/A')} stars")
        
        print("\nGetting recommendations...")
        recommendations = recommender.get_recommendations(sample_product['asin'], top_n=3)
        
        if recommendations is not None and not recommendations.empty:
            print("\nRecommended Products:")
            for _, rec in recommendations.iterrows():
                print("\n-----------------------------------")
                print(f"Title: {rec['title']}")
                print(f"Category: {rec.get('category_name', 'N/A')}")
                print(f"Price: ${rec.get('price', 'N/A')}")
                print(f"Rating: {rec.get('stars', 'N/A')} stars")
                if 'similarity_score' in rec:
                    print(f"Similarity Score: {rec['similarity_score']:.3f}")
                if 'explanation' in rec:
                    print(f"Explanation: {rec['explanation']}")
                else:
                    print("Explanation: This product has similar features that you might enjoy.")
        else:
            print("No recommendations found.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        raise

if __name__ == "__main__":
    test_recommendations()