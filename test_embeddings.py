#!/usr/bin/env python3
"""
Test script to demonstrate the new semantic embedding functionality
"""

import asyncio
import tempfile
import os
from pathlib import Path
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Import our updated semantic analyzer
try:
    from semantic_analyzer import SemanticAnalyzer
    print(" Successfully imported SemanticAnalyzer")
except ImportError as e:
    print(f" Failed to import SemanticAnalyzer: {e}")
    print("Please install the new requirements: pip install -r requirements.txt")
    exit(1)

async def create_test_files():
    """Create sample files for testing"""
    test_dir = Path("test_semantic_files")
    test_dir.mkdir(exist_ok=True)
    
    # Create sample documents with different but related content
    files = {
        "machine_learning_intro.txt": """
        Machine learning is a subset of artificial intelligence that focuses on 
        algorithms that can learn and improve from data without being explicitly programmed.
        Common techniques include supervised learning, unsupervised learning, and reinforcement learning.
        """,
        
        "ai_overview.txt": """
        Artificial intelligence encompasses machine learning, deep learning, and neural networks.
        AI systems can process data, recognize patterns, and make intelligent decisions.
        Applications include computer vision, natural language processing, and robotics.
        """,
        
        "data_science_guide.txt": """
        Data science combines statistics, programming, and domain expertise to extract
        insights from data. Key skills include data analysis, machine learning, and visualization.
        Tools commonly used are Python, R, SQL, and various ML frameworks.
        """,
        
        "cooking_recipe.txt": """
        Delicious chocolate chip cookies recipe:
        Ingredients: flour, butter, sugar, eggs, chocolate chips, vanilla extract.
        Instructions: Mix dry ingredients, cream butter and sugar, add eggs and vanilla,
        combine everything, add chocolate chips, bake at 375°F for 10-12 minutes.
        """,
        
        "travel_journal.txt": """
        Day 1 in Paris: Visited the Eiffel Tower and Louvre Museum.
        Day 2: Explored Montmartre and enjoyed croissants at a local café.
        Day 3: Seine river cruise and dinner at a traditional French bistro.
        Amazing architecture and delicious food throughout the trip.
        """
    }
    
    created_files = []
    for filename, content in files.items():
        file_path = test_dir / filename
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content.strip())
        created_files.append(str(file_path))
    
    return created_files

async def test_semantic_analysis():
    """Test the semantic analysis with and without embeddings"""
    print("\n Testing Semantic Analysis with Embeddings")
    print("=" * 50)
    
    # Create test files
    test_files = await create_test_files()
    print(f"Created {len(test_files)} test files")
    
    # Test with embeddings enabled
    print("\n Testing with Semantic Embeddings ENABLED:")
    analyzer_with_embeddings = SemanticAnalyzer(
        similarity_threshold=0.3, 
        use_embeddings=True
    )
    
    # Get embedding stats
    stats = analyzer_with_embeddings.get_embedding_stats()
    print(f"Embeddings enabled: {stats['embeddings_enabled']}")
    print(f"Model loaded: {stats['model_loaded']}")
    print(f"Model name: {stats['model_name']}")
    
    # Analyze files
    signatures_with_embeddings = await analyzer_with_embeddings.analyze_file_signatures(test_files)
    clusters_with_embeddings = analyzer_with_embeddings.find_project_clusters(signatures_with_embeddings)
    
    print(f"\nFound {len(clusters_with_embeddings)} project clusters with embeddings:")
    for i, cluster in enumerate(clusters_with_embeddings):
        print(f"  Cluster {i+1}: {cluster.project_name} (confidence: {cluster.confidence:.2f})")
        print(f"    Type: {cluster.project_type}")
        print(f"    Files: {[Path(f.path).name for f in cluster.files]}")
        print(f"    Keywords: {list(cluster.common_keywords)[:5]}")
        print()
    
    # Test without embeddings (traditional method)
    print("\n Testing with Semantic Embeddings DISABLED (Traditional):")
    analyzer_traditional = SemanticAnalyzer(
        similarity_threshold=0.3, 
        use_embeddings=False
    )
    
    signatures_traditional = await analyzer_traditional.analyze_file_signatures(test_files)
    clusters_traditional = analyzer_traditional.find_project_clusters(signatures_traditional)
    
    print(f"\nFound {len(clusters_traditional)} project clusters with traditional method:")
    for i, cluster in enumerate(clusters_traditional):
        print(f"  Cluster {i+1}: {cluster.project_name} (confidence: {cluster.confidence:.2f})")
        print(f"    Type: {cluster.project_type}")
        print(f"    Files: {[Path(f.path).name for f in cluster.files]}")
        print(f"    Keywords: {list(cluster.common_keywords)[:5]}")
        print()
    
    # Compare specific file similarities
    print("\n Detailed Similarity Comparison:")
    if len(signatures_with_embeddings) >= 3:
        # Compare ML/AI files (should be similar)
        ml_file = signatures_with_embeddings[0]  # machine_learning_intro.txt
        ai_file = signatures_with_embeddings[1]   # ai_overview.txt
        recipe_file = signatures_with_embeddings[3]  # cooking_recipe.txt
        
        # With embeddings
        embedding_sim_ml_ai = analyzer_with_embeddings._calculate_file_similarity(ml_file, ai_file)
        embedding_sim_ml_recipe = analyzer_with_embeddings._calculate_file_similarity(ml_file, recipe_file)
        
        # Without embeddings
        traditional_sim_ml_ai = analyzer_traditional._calculate_file_similarity(
            signatures_traditional[0], signatures_traditional[1]
        )
        traditional_sim_ml_recipe = analyzer_traditional._calculate_file_similarity(
            signatures_traditional[0], signatures_traditional[3]
        )
        
        print(f"ML ↔ AI similarity:")
        print(f"  With embeddings: {embedding_sim_ml_ai:.3f}")
        print(f"  Traditional: {traditional_sim_ml_ai:.3f}")
        
        print(f"ML ↔ Recipe similarity:")
        print(f"  With embeddings: {embedding_sim_ml_recipe:.3f}")
        print(f"  Traditional: {traditional_sim_ml_recipe:.3f}")
        
        print(f"\n Semantic embeddings should show higher similarity between ML/AI files")
        print(f"   and lower similarity between unrelated content (ML/Recipe)")
    
    # Show cache statistics
    final_stats = analyzer_with_embeddings.get_embedding_stats()
    print(f"\n Final Statistics:")
    print(f"Embedding cache size: {final_stats['cache_size']}")
    print(f"Keywords cache size: {final_stats['keywords_cache_size']}")
    
    # Cleanup
    import shutil
    shutil.rmtree("test_semantic_files")
    print("\n Cleaned up test files")

if __name__ == "__main__":
    print(" Semantic Embedding Test Suite")
    print("This script tests the new embedding-based semantic analysis")
    
    try:
        asyncio.run(test_semantic_analysis())
        print("\n Test completed successfully!")
    except Exception as e:
        print(f"\n Test failed: {e}")
        import traceback
        traceback.print_exc()

