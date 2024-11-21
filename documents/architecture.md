# The architecture of the Personalization Engine 

Below is a **system diagram** in Markdown, illustrating the architecture of the Personalization Engine with Redis Queue (RQ) for background tasks and data synchronization from the CDP:

```plaintext
+-----------------------------+                     +-----------------------------+
|         Client App          |                     |     Admin Dashboard        |
|     (Web/Mobile App)        |                     |    (Tenant Configuration)  |
+-----------------------------+                     +-----------------------------+
             |                                           |
             |                  API Requests             |
             |                                           |
             v                                           v
+-----------------------------+       +-------------------------------------------+
|       Load Balancer         |       |             CDP System                   |
|  (NGINX / AWS ALB)          |       |                                           |
+-----------------------------+       | +---------------------------------------+ |
             |                       | |       ArangoDB (Shared Cluster)       | |
             v                       | |   - Profile data                      | |
+-----------------------------+       | |   - Product catalogs                 | |
|         FastAPI API         |       | |   - Content catalogs                 | |
|     - Auth / Multi-tenancy   |       | +---------------------------------------+ |
|     - User Preferences       |       |                                           |
+-----------------------------+       |                                           |
             |                       +-------------------------------------------+
             |
+-----------------------------+
|      Task Queue (RQ)        | <-- Sync Triggers from CDP
|   - Background Workers      |
|   - Embedding Generation    |
+-----------------------------+
             |
+-----------------------------+
|       Qdrant Database       |
|   - Tenant Vector Indexes   |
|   - Recommendations Data    |
+-----------------------------+
             |
+-----------------------------+
|       ArangoDB Cluster      | <-- Shared with CDP
|  - User Profiles            |
|  - Product/Content Data     |
|  - Tenant Configurations    |
+-----------------------------+

Legend:
- Data Synchronization
- Real-time Requests
- Background Processing
```

The above diagram shows:

1. **Client App** and **Admin Dashboard** interact with the Personalization Engine via a **FastAPI API**.
2. **Load Balancer** (e.g., NGINX or AWS ALB) handles traffic and routes API requests to the backend.
3. **FastAPI API** is the primary gateway that:
   - Validates and authenticates requests.
   - Routes tenant-specific requests for recommendations or configurations.
4. **Redis Queue (RQ)** handles asynchronous tasks such as:
   - Syncing data from the CDP to the Personalization Engine.
   - Generating embeddings for content or user profiles.
5. **ArangoDB Cluster** is a shared data layer between the CDP and Personalization Engine. It stores:
   - User profiles.
   - Product and content catalogs.
   - Tenant-specific configurations.
6. **Qdrant Database** stores vector embeddings for personalization, with separate collections for each tenant.
7. Data synchronization ensures the **CDP** regularly updates the Personalization Engine with the latest profiles and catalog data.

This architecture ensures scalability, real-time performance, and effective multi-tenant data isolation.