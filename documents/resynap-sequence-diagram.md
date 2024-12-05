```mermaid

sequenceDiagram
    participant ReSynap RAG Agent 
    participant PostgreSQL
    participant Qdrant Vector Database
    participant AI Models
    participant Customer

    ReSynap RAG Agent ->>PostgreSQL: Store customer data
    ReSynap RAG Agent ->>ReSynap RAG Agent : Customer Analytics
    ReSynap RAG Agent ->>PostgreSQL: Update Insights
    PostgreSQL->>ReSynap RAG Agent : Provide customer insights
    ReSynap RAG Agent ->>Qdrant Vector Database: Sync data as embeddings
    Qdrant Vector Database->>ReSynap RAG Agent : Enable similarity-based searches
    ReSynap RAG Agent ->>AI Models: Train models for segmentation and personalization
    AI Models->>ReSynap RAG Agent : Provide recommendations and clusters
    ReSynap RAG Agent ->>Customer: Engage with personalized experiences
    Customer->>ReSynap RAG Agent : Interact and provide feedback
    ReSynap RAG Agent ->>AI Models: Update models with new data
    ReSynap RAG Agent ->>PostgreSQL: Save updated customer insights

