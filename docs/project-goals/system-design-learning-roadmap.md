# System Design Learning Roadmap for Grocery-Manager

## Overview
This roadmap is designed to help you master system design concepts through practical implementation in your Grocery-Manager project. Each phase builds upon the previous one, introducing new concepts as your application grows in complexity and scale.

**Current State**: Simple CRUD application with React frontend, FastAPI backend, and PostgreSQL database (Supabase). GET APIs are public; CREATE, UPDATE, DELETE are unprotected.

**Goal**: Transform this into a production-ready, scalable system while mastering all core system design concepts.

---

## Phase 1: Foundation & Core Architecture (Weeks 1-2)

### 1. Client-Server Architecture ✅ (Already Implemented)

**Why You Need It**: Your app already uses this - React frontend (client) communicates with FastAPI backend (server).

**Current State**:
- Frontend runs on `http://localhost:5173`
- Backend runs on different port with CORS enabled
- Clear separation of concerns

**What to Learn**:
- Understand request/response cycle
- Study your current CORS configuration in `backend/app/main.py:14-25`
- Document how data flows from browser → API → database → browser

**Learning Exercise**:
1. Add logging to trace a complete request lifecycle
2. Implement request/response interceptors in frontend
3. Create a diagram of your current architecture

**Success Criteria**: Can explain the complete flow of a grocery item creation from button click to database save.

---

### 2. IP Address & Networking Basics

**Why You Need It**: Understanding how clients find your server is foundational for deployment and debugging.

**Current State**: Using localhost (127.0.0.1) for development.

**Implementation Plan**:
1. **Local Network Access**:
   - Configure backend to bind to `0.0.0.0` instead of `127.0.0.1`
   - Access your app from phone/tablet on same WiFi network
   - Update CORS to allow your local IP

2. **Network Debugging**:
   - Use `ipconfig`/`ifconfig` to find your machine's IP
   - Test API calls from different devices
   - Understand private vs public IP addresses

**Practical Task**:
```python
# Update uvicorn command in backend
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

**Success Criteria**: Access your grocery app from your phone while both are on the same WiFi.

---

### 3. DNS (Domain Name System)

**Why You Need It**: Users shouldn't access `192.168.1.5:8000` - they need `grocery-manager.com`.

**Current State**: No domain, using IP addresses and localhost.

**Implementation Plan**:
1. **Local DNS Testing**:
   - Edit `/etc/hosts` file to map `grocery-local.dev` → `127.0.0.1`
   - Access app via custom domain locally

2. **Production DNS** (When deploying):
   - Buy a domain (Namecheap, Google Domains)
   - Learn DNS record types: A, CNAME, TXT
   - Configure DNS to point to your server

3. **Subdomain Strategy**:
   - `api.grocery-manager.com` → Backend
   - `grocery-manager.com` → Frontend
   - `admin.grocery-manager.com` → Admin panel (future)

**Practical Task**:
```bash
# Add to /etc/hosts
127.0.0.1 grocery-local.dev
127.0.0.1 api.grocery-local.dev

# Update frontend axios baseURL
const API_BASE_URL = 'http://api.grocery-local.dev:8000'
```

**Success Criteria**: Access your app using custom domain names locally.

---

### 4. HTTP / HTTPS Protocols

**Why You Need It**: Currently using HTTP (insecure). HTTPS encrypts data in transit - crucial for user auth and privacy.

**Current State**: Using HTTP only (`http://localhost:5173`).

**Implementation Plan**:
1. **Understand HTTP Methods**:
   - Review your CRUD operations mapping to GET, POST, PUT, DELETE
   - Study HTTP status codes you're using (200, 201, 204, 400, 404, 500)
   - Document all endpoints with proper HTTP semantics

2. **HTTPS Locally** (Development SSL):
   ```bash
   # Generate self-signed certificate
   openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes

   # Run uvicorn with SSL
   uvicorn main:app --ssl-keyfile=key.pem --ssl-certfile=cert.pem
   ```

3. **HTTPS in Production**:
   - Use Let's Encrypt for free SSL certificates
   - Configure automatic certificate renewal
   - Implement HTTP → HTTPS redirect

**Learning Focus**:
- HTTP headers (Content-Type, Authorization, Cache-Control)
- HTTPS handshake and certificate chain
- Security implications of mixed content

**Success Criteria**: All API calls work over HTTPS with valid certificates.

---

## Phase 2: API Design & Security (Weeks 3-5)

### 5. APIs

**Why You Need It**: Before REST or GraphQL, you need to understand what an API is and why it exists. APIs are the foundation of all modern software communication — every feature you add to Grocery Manager relies on them.

**What APIs Are**:
- A contract defining how software components communicate
- Abstracts implementation details behind a clean interface
- Enables frontend and backend to evolve independently

**Types of APIs** (all relevant to your grocery manager):
| Type | Protocol | Use Case in Grocery Manager |
|------|----------|----------------------------|
| REST | HTTP | Main CRUD operations (current) |
| GraphQL | HTTP | Flexible data fetching (Phase 2) |
| WebSockets | TCP | Real-time grocery list updates (Phase 6) |
| Webhooks | HTTP callbacks | External notifications (Phase 6) |

**For Grocery Manager**:
- **Public API**: GET endpoints — anyone can read grocery data
- **Private API**: POST/PUT/DELETE — only authorized users
- **Internal API**: Frontend ↔ Backend communication over HTTP

**Learning Tasks**:
1. Document every endpoint in your current backend with its HTTP method and purpose
2. Categorize them: which are public? which should be private?
3. Draw a flow diagram: Browser → React → FastAPI → Supabase → back

**Success Criteria**: Can explain what an API is, name the 4 types your grocery manager uses, and distinguish public from private endpoints.

---

### 6. REST API Principles ✅ (Partially Implemented)

**Why You Need It**: Your app already uses REST APIs, but they can be optimized and standardized.

**Current State**: RESTful endpoints exist but need refinement.

**Implementation Plan**:
1. **API Versioning**:
   ```python
   # Add version to routes
   app.include_router(api_router, prefix='/api/v1')
   ```

2. **HATEOAS (Hypermedia)**:
   ```json
   {
     "id": "123",
     "name": "Milk",
     "links": {
       "self": "/api/v1/groceries/123",
       "update": "/api/v1/groceries/123",
       "delete": "/api/v1/groceries/123"
     }
   }
   ```

3. **Standardize Response Format**:
   ```json
   {
     "success": true,
     "data": { ... },
     "message": "Grocery item created successfully",
     "timestamp": "2024-02-16T10:30:00Z"
   }
   ```

4. **Implement Proper Error Responses**:
   ```json
   {
     "success": false,
     "error": {
       "code": "GROCERY_NOT_FOUND",
       "message": "Grocery item with ID 123 not found",
       "details": {}
     }
   }
   ```

**Success Criteria**: All APIs follow consistent REST principles and return standardized responses.

---

### 7. GraphQL (Alternative to REST)

**Why You Need It**: Solve over-fetching/under-fetching problems. Frontend can request exactly what it needs.

**Use Case for Grocery Manager**:
- Mobile app needs: `{ id, name, price }` (minimal data)
- Web dashboard needs: `{ id, name, price, category, purchaseDate, expiryDate, store, notes }` (full data)
- With REST, both get the same response (wasteful)

**Implementation Plan**:
1. **Add Strawberry GraphQL to FastAPI**:
   ```python
   # Install
   pip install strawberry-graphql[fastapi]

   # Create schema
   @strawberry.type
   class Grocery:
       id: str
       name: str
       price: float
       category: str
       purchase_date: Optional[datetime]

   @strawberry.type
   class Query:
       @strawberry.field
       def grocery(self, id: str) -> Grocery:
           # Fetch from DB
           pass
   ```

2. **Implement Queries**:
   - `grocery(id: ID!)`: Get single item
   - `groceries(limit: Int, category: String)`: List with filters

3. **Implement Mutations**:
   - `createGrocery(input: CreateGroceryInput!): Grocery`
   - `updateGrocery(id: ID!, input: UpdateGroceryInput!): Grocery`

4. **Add GraphQL Playground**:
   ```python
   app.include_router(graphql_router, prefix="/graphql")
   ```

**Comparison Exercise**:
- Implement same feature in REST and GraphQL
- Measure response sizes
- Compare frontend code complexity

**Success Criteria**: GraphQL API runs alongside REST, frontend can choose either.

---

### ⚙️ Implementation Requirement: Authentication & Authorization

> **Note**: Authentication & Authorization are not one of the 30 core system design topics but are a **critical practical requirement** before deploying your REST API to production. Complete this implementation during Phase 2 before moving to Phase 3. Without it, anyone can CREATE/UPDATE/DELETE your grocery data.

**Why You Need It**:
- Identify users (Authentication)
- Control access (Authorization)
- Protect sensitive operations

**Implementation Plan**:

#### Step 1: User Management
```python
# Create User model
class User(Base):
    id = Column(UUID, primary_key=True)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime)

# Create Users table in Supabase
```

#### Step 2: JWT Authentication
```python
# Install dependencies
pip install python-jose[cryptography] passlib[bcrypt]

# Implement auth endpoints
@router.post("/auth/register")
async def register(email: str, password: str):
    # Hash password, create user
    pass

@router.post("/auth/login")
async def login(email: str, password: str):
    # Verify credentials, return JWT
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}
```

#### Step 3: Protect Routes
```python
# Add dependency
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    # Verify JWT, return user
    pass

# Protect grocery endpoints
@router.post("/groceries")
async def create_grocery(
    data: GroceryCreateSchema,
    current_user: User = Depends(get_current_user)  # 🔒 Protected
):
    # Link grocery to user
    pass
```

#### Step 4: Multi-Tenancy
```python
# Add user_id to Grocery model
class Grocery(Base):
    id = Column(UUID, primary_key=True)
    user_id = Column(UUID, ForeignKey("users.id"))  # 🔑 Link to user
    name = Column(String)
    # ... other fields

    user = relationship("User", back_populates="groceries")

# Filter queries by user
async def list_groceries(current_user: User = Depends(get_current_user)):
    return await repository.find_all(user_id=current_user.id)
```

**Success Criteria**:
- Users can register and login
- JWT tokens protect CREATE/UPDATE/DELETE
- Users only see their own groceries

---

## Phase 3: Data Layer Optimization (Weeks 5-6)

### 8. Databases (SQL) ✅ (Already Using)

**Why You Need It**: PostgreSQL provides ACID guarantees, relations, and complex queries.

**Current State**: Using Supabase (managed PostgreSQL).

**Deep Dive Tasks**:
1. **Understand ACID Properties**:
   - Test transactions with multiple grocery items
   - Implement rollback on failure

2. **Schema Design Review**:
   ```sql
   -- Current schema (example)
   CREATE TABLE groceries (
       id UUID PRIMARY KEY,
       name VARCHAR(255),
       price DECIMAL(10,2),
       category VARCHAR(100),
       purchase_date TIMESTAMP,
       expiry_date TIMESTAMP,
       created_at TIMESTAMP,
       updated_at TIMESTAMP
   );
   ```

3. **Add Relationships**:
   ```sql
   -- Categories table (normalize)
   CREATE TABLE categories (
       id UUID PRIMARY KEY,
       name VARCHAR(100) UNIQUE
   );

   -- Update groceries
   ALTER TABLE groceries
   ADD COLUMN category_id UUID REFERENCES categories(id);
   ```

**Success Criteria**: Proper normalized schema with relations.

---

### 9. SQL vs NoSQL Comparison

**Why You Need It**: Different use cases need different databases. Learn when to use each.

**Experiment**:
1. **Add MongoDB for Product Catalog**:
   - Grocery items have flexible attributes (not all fields apply to all items)
   - Use MongoDB for product metadata
   ```python
   # Install
   pip install motor  # Async MongoDB driver

   # Store flexible data
   {
     "_id": "...",
     "name": "Organic Milk",
     "attributes": {
       "brand": "Local Farm",
       "size": "1L",
       "certifications": ["Organic", "Non-GMO"],
       "nutritionFacts": { ... }  # Flexible schema
     }
   }
   ```

2. **Use Redis for Sessions**:
   ```python
   # Store JWT sessions in Redis
   await redis.setex(f"session:{user_id}", 3600, token)
   ```

**Comparison Matrix**:

| Feature | PostgreSQL | MongoDB | Redis |
|---------|-----------|---------|-------|
| Use Case | Transactional data (orders, users) | Flexible schemas (product catalog) | Caching, sessions |
| ACID | ✅ Full | ⚠️ Limited | ❌ None |
| Speed | Medium | Fast | Fastest |
| Relations | ✅ Strong | ⚠️ Manual | ❌ None |

**Success Criteria**: Use PostgreSQL for groceries, MongoDB for product catalog, Redis for caching.

---

### 10. Database Indexing

**Why You Need It**: As grocery list grows (1000s of items), queries slow down. Indexes speed up lookups.

**Problem Scenario**:
```python
# Slow query without index
SELECT * FROM groceries
WHERE user_id = '123' AND category = 'Dairy'
ORDER BY expiry_date;
# Takes 2 seconds with 10,000 rows
```

**Implementation**:
```sql
-- Add indexes
CREATE INDEX idx_groceries_user_id ON groceries(user_id);
CREATE INDEX idx_groceries_category ON groceries(category);
CREATE INDEX idx_groceries_expiry ON groceries(expiry_date);

-- Composite index for common query
CREATE INDEX idx_user_category_expiry
ON groceries(user_id, category, expiry_date);

-- Query now takes 20ms ⚡
```

**Learning Tasks**:
1. Use `EXPLAIN ANALYZE` to see query plans
2. Identify slow queries in your app
3. Add indexes strategically
4. Understand index trade-offs (write speed vs read speed)

**Practical Exercise**:
```python
# Add 10,000 test groceries
# Measure query time before/after indexing
import time

start = time.time()
results = await db.execute("SELECT * FROM groceries WHERE user_id = '...'")
print(f"Query took {time.time() - start}s")
```

**Success Criteria**: All common queries use indexes and run under 100ms.

---

### 11. Database Replication

**Why You Need It**:
- **High Availability**: If primary DB crashes, replica takes over
- **Read Scaling**: Send read queries to replicas, writes to primary
- **Disaster Recovery**: Replicas serve as backups

**Use Case for Grocery Manager**:
- 90% of operations are reads (viewing grocery lists)
- 10% are writes (adding/updating items)
- Use replicas to scale read traffic

**Implementation with Supabase**:
1. **Configure Read Replicas**:
   - Supabase provides replication in higher tiers
   - Set up primary (write) and replica (read) connections

2. **Update Database Connection**:
   ```python
   # database.py
   PRIMARY_DB_URL = "postgresql://..."  # Write operations
   REPLICA_DB_URL = "postgresql://replica..."  # Read operations

   class DatabaseRouter:
       def get_connection(self, operation: str):
           if operation in ['INSERT', 'UPDATE', 'DELETE']:
               return PRIMARY_DB_URL
           else:  # SELECT
               return REPLICA_DB_URL
   ```

3. **Handle Replication Lag**:
   ```python
   # After creating a grocery item
   await primary_db.insert(grocery)

   # Immediate read might not see it yet (replication lag)
   # Solution: Read from primary for user's own writes
   if user_id == current_user.id:
       result = await primary_db.select(...)  # Read from primary
   else:
       result = await replica_db.select(...)  # Read from replica
   ```

**Monitoring**:
```python
# Check replication lag
SELECT now() - pg_last_xact_replay_timestamp() AS replication_lag;
```

**Success Criteria**:
- Read queries use replicas
- Write queries use primary
- Replication lag monitored and under 1 second

---

### 12. Database Sharding

**Why You Need It**: Single database server hits limits (disk, CPU, memory). Sharding splits data across multiple servers.

**Use Case for Grocery Manager**:
- 1 million users, each with 100 grocery items = 100 million rows
- Single DB server maxes out at ~10 million rows with good performance
- Need to split data across multiple databases

**Sharding Strategy - User-Based (Horizontal Sharding)**:
```python
# Shard by user_id
# Users A-M → Database 1
# Users N-Z → Database 2

def get_shard(user_id: str) -> str:
    """Determine which shard to use based on user_id"""
    first_char = user_id[0].lower()
    if first_char <= 'm':
        return "DB_SHARD_1"
    else:
        return "DB_SHARD_2"

# Usage
@router.get("/groceries")
async def list_groceries(current_user: User = Depends(get_current_user)):
    shard = get_shard(current_user.id)
    db_connection = get_db_connection(shard)
    groceries = await db_connection.execute("SELECT * FROM groceries WHERE user_id = ?")
    return groceries
```

**Alternative: Hash-Based Sharding**:
```python
def get_shard_by_hash(user_id: str, num_shards: int = 4) -> int:
    """Consistent hashing for even distribution"""
    return hash(user_id) % num_shards

# User 'abc123' → Shard 2
# User 'def456' → Shard 3
```

**Implementation Steps**:
1. **Set up multiple PostgreSQL instances**
2. **Create routing layer**:
   ```python
   class ShardManager:
       def __init__(self):
           self.shards = {
               0: create_engine("postgresql://shard0..."),
               1: create_engine("postgresql://shard1..."),
               2: create_engine("postgresql://shard2..."),
               3: create_engine("postgresql://shard3..."),
           }

       def get_shard(self, user_id: str):
           shard_id = hash(user_id) % len(self.shards)
           return self.shards[shard_id]
   ```

3. **Handle Cross-Shard Queries** (Complex):
   ```python
   # Problem: Get all expired items across all shards
   async def get_all_expired_items():
       results = []
       for shard in shard_manager.shards.values():
           shard_results = await shard.execute(
               "SELECT * FROM groceries WHERE expiry_date < NOW()"
           )
           results.extend(shard_results)
       return results
   ```

**Challenges**:
- Joins across shards are expensive
- Transactions across shards are complex
- Rebalancing when adding new shards

**Success Criteria**:
- Data evenly distributed across shards
- Queries route to correct shard
- Cross-shard operations handled correctly

---

### 13. Vertical Partitioning

**Why You Need It**: Split tables by columns instead of rows. Separate frequently accessed data from rarely accessed data.

**Use Case for Grocery Manager**:
```python
# Current Grocery table (wide table)
class Grocery(Base):
    id = Column(UUID, primary_key=True)

    # Frequently accessed
    name = Column(String)
    price = Column(Decimal)
    category = Column(String)
    expiry_date = Column(DateTime)

    # Rarely accessed (details)
    store_name = Column(String)
    brand = Column(String)
    barcode = Column(String)
    nutritional_info = Column(JSON)  # Large field
    purchase_receipt = Column(Text)  # Large field
    notes = Column(Text)
```

**Problem**: Loading grocery list fetches ALL columns, including large unused fields (nutritional_info, receipt).

**Solution - Vertical Partitioning**:
```python
# Table 1: Frequently accessed (hot data)
class Grocery(Base):
    __tablename__ = 'groceries'

    id = Column(UUID, primary_key=True)
    name = Column(String, index=True)
    price = Column(Decimal)
    category = Column(String, index=True)
    expiry_date = Column(DateTime, index=True)
    user_id = Column(UUID, ForeignKey('users.id'))

# Table 2: Rarely accessed (cold data)
class GroceryDetails(Base):
    __tablename__ = 'grocery_details'

    grocery_id = Column(UUID, ForeignKey('groceries.id'), primary_key=True)
    store_name = Column(String)
    brand = Column(String)
    barcode = Column(String)
    nutritional_info = Column(JSON)
    purchase_receipt = Column(Text)
    notes = Column(Text)
```

**Query Optimization**:
```python
# Fast: List view (only hot data)
@router.get("/groceries")
async def list_groceries():
    groceries = await db.execute(
        "SELECT id, name, price, category FROM groceries WHERE user_id = ?"
    )
    return groceries  # Fast, small payload

# Slow: Detail view (join when needed)
@router.get("/groceries/{id}")
async def get_grocery_detail(id: str):
    grocery = await db.execute("""
        SELECT g.*, gd.*
        FROM groceries g
        LEFT JOIN grocery_details gd ON g.id = gd.grocery_id
        WHERE g.id = ?
    """)
    return grocery
```

**Benefits**:
- List queries 10x faster (smaller rows)
- Better cache utilization
- Reduced I/O for common operations

**Success Criteria**:
- Hot and cold data separated
- List queries don't load detail fields
- Detail page loads only when needed

---

## Phase 4: Performance & Caching (Weeks 7-8)

### 14. Caching Strategies

**Why You Need It**: Database queries are slow. Caching stores frequently accessed data in memory for instant retrieval.

**Use Cases for Grocery Manager**:
- User's grocery list (read frequently, updated rarely)
- Product catalog (changes infrequently)
- Category list (static data)

**Implementation with Redis**:

#### Step 1: Set up Redis
```bash
# Install Redis
docker run -d -p 6379:6379 redis:alpine

# Install Python client
pip install redis aioredis
```

#### Step 2: Implement Cache Layer
```python
from redis import asyncio as aioredis
import json

class CacheService:
    def __init__(self):
        self.redis = aioredis.from_url("redis://localhost:6379")

    async def get(self, key: str):
        value = await self.redis.get(key)
        return json.loads(value) if value else None

    async def set(self, key: str, value: any, ttl: int = 3600):
        await self.redis.setex(key, ttl, json.dumps(value))

    async def delete(self, key: str):
        await self.redis.delete(key)

# Usage in service
class GroceryService:
    def __init__(self, cache: CacheService):
        self.cache = cache

    async def get_grocery(self, grocery_id: str):
        # Try cache first
        cache_key = f"grocery:{grocery_id}"
        cached = await self.cache.get(cache_key)
        if cached:
            return cached  # Cache hit ⚡

        # Cache miss - fetch from DB
        grocery = await self.repository.find_by_id(grocery_id)

        # Store in cache
        await self.cache.set(cache_key, grocery, ttl=3600)
        return grocery
```

#### Step 3: Cache Invalidation (Hardest Problem in CS)
```python
async def update_grocery(self, grocery_id: str, data: dict):
    # Update database
    updated = await self.repository.update(grocery_id, data)

    # Invalidate cache
    await self.cache.delete(f"grocery:{grocery_id}")
    await self.cache.delete(f"user:{updated.user_id}:groceries")  # List cache

    return updated
```

#### Step 4: Cache-Aside Pattern
```python
# Pattern: Application manages cache
async def list_groceries(self, user_id: str):
    cache_key = f"user:{user_id}:groceries"

    # 1. Check cache
    cached = await self.cache.get(cache_key)
    if cached:
        return cached

    # 2. Fetch from DB
    groceries = await self.repository.find_all(user_id=user_id)

    # 3. Update cache
    await self.cache.set(cache_key, groceries, ttl=300)  # 5 min TTL

    return groceries
```

**Caching Strategies**:

1. **Cache-Aside**: App manages cache (implemented above)
2. **Write-Through**: Write to cache + DB simultaneously
3. **Write-Behind**: Write to cache, async write to DB
4. **Refresh-Ahead**: Proactively refresh expiring cache

**Monitoring**:
```python
# Track cache hit rate
@router.get("/cache/stats")
async def get_cache_stats():
    info = await redis.info()
    hits = info['keyspace_hits']
    misses = info['keyspace_misses']
    hit_rate = hits / (hits + misses) * 100
    return {"hit_rate": f"{hit_rate:.2f}%"}
```

**Success Criteria**:
- Cache hit rate > 80%
- List queries return in <10ms (from cache)
- Proper cache invalidation on updates

---

### 15. Denormalization

**Why You Need It**: Normalized databases require joins, which are slow. Denormalization trades space for speed.

**Use Case - Grocery Statistics Dashboard**:

**Problem with Normalization**:
```sql
-- Normalized schema (slow query)
SELECT
    u.name,
    COUNT(g.id) as total_items,
    SUM(g.price) as total_spent,
    c.name as top_category
FROM users u
JOIN groceries g ON u.id = g.user_id
JOIN categories c ON g.category_id = c.id
GROUP BY u.id
-- This join is expensive with millions of rows!
```

**Solution - Denormalized Stats Table**:
```python
# Create denormalized table
class UserGroceryStats(Base):
    __tablename__ = 'user_grocery_stats'

    user_id = Column(UUID, primary_key=True)
    total_items = Column(Integer, default=0)
    total_spent = Column(Decimal, default=0)
    top_category = Column(String)
    last_purchase_date = Column(DateTime)
    updated_at = Column(DateTime)

# Update stats when groceries change
async def create_grocery(self, data: GroceryCreateSchema):
    # 1. Create grocery item
    grocery = await self.repository.create(data)

    # 2. Update denormalized stats (same transaction)
    await self.db.execute("""
        UPDATE user_grocery_stats
        SET
            total_items = total_items + 1,
            total_spent = total_spent + :price,
            last_purchase_date = NOW()
        WHERE user_id = :user_id
    """, {"price": grocery.price, "user_id": grocery.user_id})

    return grocery

# Fast dashboard query (no joins!)
async def get_user_dashboard(user_id: str):
    stats = await db.execute("""
        SELECT * FROM user_grocery_stats WHERE user_id = :user_id
    """, {"user_id": user_id})
    return stats  # Instant response ⚡
```

**Another Example - Storing Category Name**:
```python
# Instead of:
class Grocery:
    category_id = Column(UUID, ForeignKey('categories.id'))  # Needs join

# Denormalize:
class Grocery:
    category_id = Column(UUID, ForeignKey('categories.id'))
    category_name = Column(String)  # Denormalized! No join needed

# Trade-off: Must update category_name if category changes
async def update_category_name(category_id: str, new_name: str):
    # Update categories table
    await db.execute("UPDATE categories SET name = ? WHERE id = ?")

    # Update denormalized data in groceries table
    await db.execute(
        "UPDATE groceries SET category_name = ? WHERE category_id = ?",
        (new_name, category_id)
    )
```

**When to Denormalize**:
- ✅ Read-heavy operations (dashboards, reports)
- ✅ Data rarely changes (category names)
- ✅ Query performance critical
- ❌ Write-heavy operations
- ❌ Frequently changing data

**Success Criteria**: Dashboard loads in <100ms without complex joins.

---

### 16. Latency Optimization

**Why You Need It**: Users expect instant responses. Every 100ms delay = 1% drop in conversions.

**Measure Current Latency**:
```python
from fastapi import Request
import time

@app.middleware("http")
async def add_latency_header(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    latency = (time.time() - start) * 1000  # ms
    response.headers["X-Response-Time"] = f"{latency:.2f}ms"
    return response
```

**Optimization Strategies**:

#### 1. Database Query Optimization
```python
# Bad: N+1 query problem
groceries = await db.execute("SELECT * FROM groceries")
for grocery in groceries:
    category = await db.execute(
        "SELECT * FROM categories WHERE id = ?", grocery.category_id
    )  # N additional queries!

# Good: Join or eager loading
groceries = await db.execute("""
    SELECT g.*, c.name as category_name
    FROM groceries g
    JOIN categories c ON g.category_id = c.id
""")  # Single query
```

#### 2. API Response Compression
```python
from fastapi.responses import Response
import gzip

@app.middleware("http")
async def compress_response(request: Request, call_next):
    response = await call_next(request)
    if "gzip" in request.headers.get("accept-encoding", ""):
        # Compress response
        content = gzip.compress(response.body)
        return Response(
            content=content,
            headers={"Content-Encoding": "gzip"}
        )
    return response
```

#### 3. Lazy Loading
```python
# Don't fetch details until needed
@router.get("/groceries/{id}")
async def get_grocery(id: str, include_details: bool = False):
    grocery = await repo.find_by_id(id)

    if include_details:
        grocery.details = await repo.get_details(id)

    return grocery
```

#### 4. Connection Pooling
```python
# Bad: New connection per request
async def get_grocery():
    conn = await asyncpg.connect("postgresql://...")
    result = await conn.fetch("SELECT ...")
    await conn.close()

# Good: Reuse connections from pool
from sqlalchemy.ext.asyncio import create_async_engine

engine = create_async_engine(
    "postgresql://...",
    pool_size=20,  # Connection pool
    max_overflow=10
)
```

**Latency Budget**:
- Database query: < 50ms
- Business logic: < 20ms
- Serialization: < 10ms
- Network: < 20ms
- **Total: < 100ms**

**Success Criteria**: 95th percentile latency < 100ms.

---

## Phase 5: Scalability & Distribution (Weeks 9-11)

### 17. Vertical Scaling

**Why You Need It**: Your app is slow. Easiest solution: Add more resources to existing server.

**Current State**: Running on single server with limited resources.

**Implementation**:

#### Step 1: Identify Bottleneck
```python
# Monitor resource usage
import psutil

@router.get("/health")
async def health_check():
    return {
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent
    }
```

#### Step 2: Upgrade Resources
```bash
# Current: 2 CPU, 4GB RAM
# Upgrade to: 8 CPU, 32GB RAM

# For cloud deployments:
# AWS: Change instance type (t3.medium → t3.2xlarge)
# DigitalOcean: Resize droplet
# Heroku: Upgrade dyno type
```

#### Step 3: Optimize for More Resources
```python
# Increase worker processes
uvicorn main:app --workers 8  # Match CPU count

# Increase database connections
engine = create_async_engine(
    DATABASE_URL,
    pool_size=50,  # Increased from 20
    max_overflow=25
)

# Increase cache size
redis.config_set("maxmemory", "4gb")
```

**Limitations**:
- ❌ Hardware limits (can't infinitely scale single machine)
- ❌ Expensive (16 CPU machine costs 4x more than 4 CPU)
- ❌ Single point of failure
- ✅ Easy to implement
- ✅ No code changes needed

**Success Criteria**: Server handles 2x traffic with hardware upgrade.

---

### 18. Horizontal Scaling

**Why You Need It**: Vertical scaling hits limits. Horizontal scaling adds more servers.

**Architecture Change**:
```
Before:
[Client] → [Single Server] → [Database]

After:
[Client] → [Load Balancer] → [Server 1] → [Database]
                           → [Server 2]
                           → [Server 3]
```

**Implementation**:

#### Step 1: Make App Stateless
```python
# Bad: Store session in memory
sessions = {}  # Lost when server restarts!

def login(user_id: str):
    sessions[user_id] = {"logged_in": True}

# Good: Store session in Redis (shared state)
async def login(user_id: str):
    await redis.set(f"session:{user_id}", {"logged_in": True})
```

#### Step 2: Deploy Multiple Instances
```bash
# Start 3 instances on different ports
uvicorn main:app --port 8000 &
uvicorn main:app --port 8001 &
uvicorn main:app --port 8002 &
```

#### Step 3: Add Load Balancer (see next section)

**Requirements for Horizontal Scaling**:
1. ✅ Stateless application (use Redis for sessions)
2. ✅ Shared database (all instances use same DB)
3. ✅ Shared cache (all instances use same Redis)
4. ✅ Shared file storage (use S3/Blob storage, not local disk)

**Success Criteria**:
- 3+ backend instances running
- Traffic distributed evenly
- Session persists across servers

---

### 19. Load Balancers

**Why You Need It**: Distribute traffic across multiple backend servers. Essential for horizontal scaling.

**Implementation with Nginx**:

```nginx
# nginx.conf
upstream grocery_backend {
    # Load balancing strategies
    least_conn;  # Send to server with least connections

    server localhost:8000 weight=1;
    server localhost:8001 weight=1;
    server localhost:8002 weight=2;  # More powerful server
}

server {
    listen 80;
    server_name api.grocery-manager.com;

    location / {
        proxy_pass http://grocery_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;

        # Health check
        proxy_next_upstream error timeout http_500;
    }
}
```

**Load Balancing Algorithms**:

1. **Round Robin** (default):
   ```
   Request 1 → Server 1
   Request 2 → Server 2
   Request 3 → Server 3
   Request 4 → Server 1 (cycle repeats)
   ```

2. **Least Connections**:
   - Send to server with fewest active connections
   - Better for long-running requests

3. **IP Hash** (Sticky Sessions):
   ```nginx
   upstream grocery_backend {
       ip_hash;  # Same client always goes to same server
       server localhost:8000;
       server localhost:8001;
   }
   ```

**Health Checks**:
```python
# Add health endpoint
@app.get("/health")
async def health():
    # Check database connection
    try:
        await db.execute("SELECT 1")
        return {"status": "healthy"}
    except:
        raise HTTPException(status_code=503, detail="Database unavailable")
```

```nginx
# Nginx config
upstream grocery_backend {
    server localhost:8000 max_fails=3 fail_timeout=30s;
    server localhost:8001 max_fails=3 fail_timeout=30s;

    # If server fails 3 times, remove for 30 seconds
}
```

**Cloud Load Balancers**:
- AWS: Application Load Balancer (ALB)
- Google Cloud: Cloud Load Balancing
- Azure: Azure Load Balancer

**Success Criteria**:
- Traffic evenly distributed
- Failed servers automatically removed
- Zero downtime deployments

---

### 20. Proxy / Reverse Proxy

**Why You Need It**: Proxies sit between clients and servers, controlling traffic flow. There are two types — understanding both changes how you think about network architecture.

**Forward Proxy** (client-side):
- Sits between the client and the internet
- Client sends all requests through the proxy
- Use cases: anonymity, content filtering, corporate firewalls
- Example: A VPN or Squid proxy

```
[Browser] → [Forward Proxy] → [Internet] → [Server]
```

**Reverse Proxy** (server-side):
- Sits between the internet and your backend servers
- Clients don't know which server actually handles their request
- Use cases: load balancing, SSL termination, caching, security

```
[Browser] → [Reverse Proxy (Nginx)] → [Backend Server 1]
                                     → [Backend Server 2]
```

**For Grocery Manager** — you will use a **reverse proxy** (Nginx) to:
- Hide backend servers from public internet
- SSL termination (encrypt/decrypt HTTPS at proxy)
- Cache static content
- Rate limiting and DDoS protection
- Serve frontend files

**Nginx as Reverse Proxy**:

```nginx
# Full configuration
server {
    listen 80;
    server_name grocery-manager.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name grocery-manager.com;

    # SSL certificates
    ssl_certificate /etc/ssl/certs/grocery-manager.crt;
    ssl_certificate_key /etc/ssl/private/grocery-manager.key;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN";
    add_header X-Content-Type-Options "nosniff";
    add_header X-XSS-Protection "1; mode=block";

    # Cache static files
    location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Proxy API requests
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Serve frontend
    location / {
        root /var/www/grocery-frontend/dist;
        try_files $uri $uri/ /index.html;
    }
}
```

**Benefits**:
- 🔒 SSL termination (backend handles plain HTTP)
- ⚡ Static file caching
- 🛡️ Hide backend infrastructure
- 📊 Centralized logging

**Success Criteria**:
- All traffic goes through Nginx
- SSL handled at proxy
- Static files cached

---

## Phase 6: Advanced Patterns (Weeks 12-15)

### 21. Microservices Architecture

**Why You Need It**: Monolith becomes hard to maintain. Split into smaller, independent services.

**Current Monolith**:
```
grocery-manager/
  backend/
    - auth
    - grocery CRUD
    - user management
    - notifications
    - reports
    - payments
```

**Microservices Split**:
```
auth-service/          # Port 8001
  - User authentication
  - JWT issuing

grocery-service/       # Port 8002
  - Grocery CRUD
  - Categories

notification-service/  # Port 8003
  - Email notifications
  - Push notifications

analytics-service/     # Port 8004
  - Usage reports
  - Statistics

payment-service/       # Port 8005
  - Process payments
  - Subscriptions
```

**Implementation**:

#### Step 1: Extract Auth Service
```python
# auth-service/main.py
from fastapi import FastAPI

app = FastAPI(title="Auth Service")

@app.post("/auth/login")
async def login(email: str, password: str):
    # Authenticate user
    user = await verify_credentials(email, password)
    token = create_jwt(user.id)
    return {"access_token": token}

@app.post("/auth/verify")
async def verify_token(token: str):
    # Verify JWT
    payload = decode_jwt(token)
    return {"user_id": payload["sub"]}
```

#### Step 2: Inter-Service Communication
```python
# grocery-service needs to verify user
import httpx

async def verify_user(token: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://auth-service:8001/auth/verify",
            json={"token": token}
        )
        return response.json()

@router.post("/groceries")
async def create_grocery(data: dict, token: str):
    # Call auth service
    user = await verify_user(token)

    # Create grocery
    grocery = await repo.create(data)
    return grocery
```

#### Step 3: API Gateway
```python
# api-gateway/main.py
from fastapi import FastAPI, Request
import httpx

app = FastAPI()

SERVICES = {
    "auth": "http://localhost:8001",
    "grocery": "http://localhost:8002",
    "notification": "http://localhost:8003"
}

@app.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy(service: str, path: str, request: Request):
    # Route to appropriate service
    url = f"{SERVICES[service]}/{path}"

    async with httpx.AsyncClient() as client:
        response = await client.request(
            method=request.method,
            url=url,
            content=await request.body(),
            headers=dict(request.headers)
        )
    return response.json()

# Clients call:
# POST /auth/login → routed to auth-service
# GET /grocery/items → routed to grocery-service
```

**Benefits**:
- ✅ Independent deployment
- ✅ Technology diversity (Python, Node, Go)
- ✅ Team autonomy
- ❌ Complexity (distributed system)
- ❌ Network latency between services

**Success Criteria**:
- 3+ independent services running
- Services communicate via HTTP/gRPC
- Each service has own database

---

### 22. Message Queues

**Why You Need It**:
- Decouple services (async communication)
- Handle traffic spikes (buffer requests)
- Retry failed operations

**Use Cases for Grocery Manager**:

1. **Email Notifications**: Don't wait for email to send
2. **Report Generation**: Heavy computation runs async
3. **Data Analytics**: Process events in background

**Implementation with RabbitMQ**:

#### Step 1: Set up RabbitMQ
```bash
docker run -d -p 5672:5672 -p 15672:15672 rabbitmq:management
```

#### Step 2: Publish Events
```python
# grocery-service publishes event when item created
import aio_pika

async def create_grocery(data: dict):
    # Save to database
    grocery = await repo.create(data)

    # Publish event to queue
    connection = await aio_pika.connect_robust("amqp://localhost")
    channel = await connection.channel()

    await channel.default_exchange.publish(
        aio_pika.Message(
            body=json.dumps({
                "event": "grocery.created",
                "data": {
                    "grocery_id": grocery.id,
                    "user_id": grocery.user_id,
                    "name": grocery.name
                }
            }).encode()
        ),
        routing_key="grocery_events"
    )

    return grocery  # Return immediately, don't wait for notification
```

#### Step 3: Consume Events
```python
# notification-service consumes events
async def consume_grocery_events():
    connection = await aio_pika.connect_robust("amqp://localhost")
    channel = await connection.channel()
    queue = await channel.declare_queue("grocery_events", durable=True)

    async for message in queue:
        async with message.process():
            event = json.loads(message.body)

            if event["event"] == "grocery.created":
                # Send email notification
                await send_email(
                    event["data"]["user_id"],
                    f"Grocery item {event['data']['name']} added!"
                )
```

**Patterns**:

1. **Work Queue**: Distribute tasks among workers
   ```
   [Producer] → [Queue] → [Worker 1]
                       → [Worker 2]
                       → [Worker 3]
   ```

2. **Pub/Sub**: Multiple consumers for same message
   ```
   [Publisher] → [Exchange] → [Queue 1] → [Email Service]
                           → [Queue 2] → [SMS Service]
                           → [Queue 3] → [Analytics Service]
   ```

**Dead Letter Queue** (for failed messages):
```python
await channel.declare_queue(
    "grocery_events",
    arguments={
        "x-dead-letter-exchange": "dlx",
        "x-message-ttl": 60000  # 60 seconds
    }
)
```

**Success Criteria**:
- Async operations don't block API responses
- Failed jobs automatically retry
- System handles traffic spikes

---

### 23. Rate Limiting

**Why You Need It**:
- Prevent abuse (DoS attacks)
- Fair resource allocation
- Cost control (API quotas)

**Use Cases**:
- Free users: 100 requests/hour
- Premium users: 1000 requests/hour
- Prevent brute force login attempts

**Implementation**:

#### Step 1: Token Bucket Algorithm
```python
from fastapi import Request, HTTPException
import redis.asyncio as redis
import time

class RateLimiter:
    def __init__(self, redis_client):
        self.redis = redis_client

    async def check_rate_limit(
        self,
        key: str,
        max_requests: int,
        window_seconds: int
    ) -> bool:
        """Token bucket algorithm"""
        now = time.time()
        window_start = now - window_seconds

        # Remove old requests
        await self.redis.zremrangebyscore(key, 0, window_start)

        # Count requests in current window
        request_count = await self.redis.zcard(key)

        if request_count >= max_requests:
            return False  # Rate limit exceeded

        # Add current request
        await self.redis.zadd(key, {str(now): now})
        await self.redis.expire(key, window_seconds)

        return True

# Middleware
@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    user_id = request.headers.get("X-User-ID", request.client.host)
    key = f"rate_limit:{user_id}"

    # 100 requests per hour
    allowed = await rate_limiter.check_rate_limit(key, 100, 3600)

    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Try again later."
        )

    response = await call_next(request)

    # Add rate limit headers
    remaining = 100 - await redis.zcard(key)
    response.headers["X-RateLimit-Limit"] = "100"
    response.headers["X-RateLimit-Remaining"] = str(remaining)

    return response
```

#### Step 2: User-Based Rate Limits
```python
# Different limits for different user tiers
async def get_rate_limit(user: User) -> tuple[int, int]:
    if user.tier == "free":
        return (100, 3600)  # 100/hour
    elif user.tier == "premium":
        return (1000, 3600)  # 1000/hour
    else:
        return (10000, 3600)  # 10000/hour

@app.middleware("http")
async def rate_limit_by_user(request: Request, call_next):
    user = await get_current_user(request)
    max_requests, window = await get_rate_limit(user)

    allowed = await rate_limiter.check_rate_limit(
        f"rate_limit:{user.id}",
        max_requests,
        window
    )

    if not allowed:
        raise HTTPException(status_code=429)

    return await call_next(request)
```

#### Step 3: Endpoint-Specific Limits
```python
# Stricter limits for sensitive endpoints
@router.post("/auth/login")
@limiter.limit("5/minute")  # Only 5 login attempts per minute
async def login(email: str, password: str):
    pass

@router.get("/groceries")
@limiter.limit("100/minute")  # Generous for read operations
async def list_groceries():
    pass
```

**Alternative: Use Nginx**:
```nginx
# Rate limit at reverse proxy level
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

location /api/ {
    limit_req zone=api_limit burst=20 nodelay;
    proxy_pass http://backend;
}
```

**Success Criteria**:
- API returns 429 when limit exceeded
- Different limits for different users
- Rate limit headers in response

---

### 24. API Gateway

**Why You Need It**: Single entry point for all microservices. Handles cross-cutting concerns.

**Responsibilities**:
- ✅ Authentication/Authorization
- ✅ Rate limiting
- ✅ Request routing
- ✅ Load balancing
- ✅ Caching
- ✅ Monitoring/Logging

**Implementation with Kong**:

```bash
# Install Kong
docker run -d --name kong \
  -e "KONG_DATABASE=off" \
  -e "KONG_PROXY_ACCESS_LOG=/dev/stdout" \
  -e "KONG_ADMIN_ACCESS_LOG=/dev/stdout" \
  -e "KONG_PROXY_ERROR_LOG=/dev/stderr" \
  -e "KONG_ADMIN_ERROR_LOG=/dev/stderr" \
  -e "KONG_ADMIN_LISTEN=0.0.0.0:8001" \
  -p 8000:8000 \
  -p 8001:8001 \
  kong:latest
```

**Configure Routes**:
```bash
# Add grocery service route
curl -X POST http://localhost:8001/services \
  --data name=grocery-service \
  --data url='http://localhost:8002'

curl -X POST http://localhost:8001/services/grocery-service/routes \
  --data 'paths[]=/groceries'

# Add auth service route
curl -X POST http://localhost:8001/services \
  --data name=auth-service \
  --data url='http://localhost:8001'

curl -X POST http://localhost:8001/services/auth-service/routes \
  --data 'paths[]=/auth'
```

**Add Plugins**:
```bash
# Rate limiting plugin
curl -X POST http://localhost:8001/services/grocery-service/plugins \
  --data "name=rate-limiting" \
  --data "config.minute=100"

# JWT authentication plugin
curl -X POST http://localhost:8001/services/grocery-service/plugins \
  --data "name=jwt"

# CORS plugin
curl -X POST http://localhost:8001/services/grocery-service/plugins \
  --data "name=cors" \
  --data "config.origins=*"
```

**Custom API Gateway (FastAPI)**:
```python
from fastapi import FastAPI, Request, HTTPException
import httpx

app = FastAPI(title="Grocery API Gateway")

# Service registry
SERVICES = {
    "auth": "http://localhost:8001",
    "grocery": "http://localhost:8002",
    "notification": "http://localhost:8003"
}

# Middleware: Authentication
@app.middleware("http")
async def authenticate(request: Request, call_next):
    # Skip auth for login endpoint
    if request.url.path == "/auth/login":
        return await call_next(request)

    # Verify JWT
    token = request.headers.get("Authorization", "").replace("Bearer ", "")
    if not token:
        raise HTTPException(status_code=401, detail="Missing token")

    # Validate with auth service
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{SERVICES['auth']}/auth/verify",
            json={"token": token}
        )
        if response.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid token")

    # Add user info to request state
    request.state.user = response.json()
    return await call_next(request)

# Route: Proxy requests
@app.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy(service: str, path: str, request: Request):
    if service not in SERVICES:
        raise HTTPException(status_code=404, detail="Service not found")

    target_url = f"{SERVICES[service]}/{path}"

    # Forward request to target service
    async with httpx.AsyncClient() as client:
        response = await client.request(
            method=request.method,
            url=target_url,
            headers=dict(request.headers),
            content=await request.body(),
            params=dict(request.query_params)
        )

    return Response(
        content=response.content,
        status_code=response.status_code,
        headers=dict(response.headers)
    )
```

**Success Criteria**:
- All client requests go through gateway
- Authentication enforced at gateway
- Services don't handle auth themselves

---

### 25. WebSockets (Real-Time Updates)

**Why You Need It**: HTTP is request/response. WebSockets enable real-time, bidirectional communication.

**Use Cases for Grocery Manager**:
- Live grocery list updates (when family member adds item)
- Real-time price change notifications
- Collaborative shopping lists

**Implementation**:

#### Step 1: Add WebSocket Endpoint
```python
from fastapi import WebSocket, WebSocketDisconnect

class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[str, list[WebSocket]] = {}

    async def connect(self, user_id: str, websocket: WebSocket):
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)

    async def disconnect(self, user_id: str, websocket: WebSocket):
        self.active_connections[user_id].remove(websocket)

    async def send_to_user(self, user_id: str, message: dict):
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                await connection.send_json(message)

manager = ConnectionManager()

@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await manager.connect(user_id, websocket)
    try:
        while True:
            # Keep connection alive
            data = await websocket.receive_text()
            # Echo back (optional)
            await websocket.send_text(f"Message received: {data}")
    except WebSocketDisconnect:
        await manager.disconnect(user_id, websocket)
```

#### Step 2: Notify on Changes
```python
@router.post("/groceries")
async def create_grocery(data: dict, current_user: User = Depends(get_current_user)):
    # Create grocery
    grocery = await service.create_grocery(data)

    # Notify all connected clients for this user
    await manager.send_to_user(current_user.id, {
        "event": "grocery.created",
        "data": grocery
    })

    return grocery
```

#### Step 3: Frontend WebSocket Client
```typescript
// React hook for WebSocket
import { useEffect, useState } from 'react';

function useGroceryWebSocket(userId: string) {
  const [groceries, setGroceries] = useState([]);

  useEffect(() => {
    const ws = new WebSocket(`ws://localhost:8000/ws/${userId}`);

    ws.onmessage = (event) => {
      const message = JSON.parse(event.data);

      if (message.event === 'grocery.created') {
        setGroceries(prev => [...prev, message.data]);
      } else if (message.event === 'grocery.updated') {
        setGroceries(prev => prev.map(g =>
          g.id === message.data.id ? message.data : g
        ));
      } else if (message.event === 'grocery.deleted') {
        setGroceries(prev => prev.filter(g => g.id !== message.data.id));
      }
    };

    return () => ws.close();
  }, [userId]);

  return groceries;
}
```

**Scaling WebSockets**:
```python
# Use Redis pub/sub for multi-server WebSocket
import aioredis

redis = aioredis.from_url("redis://localhost")

@router.post("/groceries")
async def create_grocery(data: dict):
    grocery = await service.create_grocery(data)

    # Publish to Redis
    await redis.publish(
        f"user:{grocery.user_id}",
        json.dumps({"event": "grocery.created", "data": grocery})
    )

    return grocery

# WebSocket server subscribes to Redis
async def redis_listener(user_id: str):
    pubsub = redis.pubsub()
    await pubsub.subscribe(f"user:{user_id}")

    async for message in pubsub.listen():
        if message["type"] == "message":
            data = json.loads(message["data"])
            await manager.send_to_user(user_id, data)
```

**Success Criteria**:
- Real-time updates without page refresh
- Multiple clients stay in sync
- Works across multiple servers

---

### 26. WebHooks (Outbound Notifications)

**Why You Need It**: Notify external systems when events occur in your app.

**Use Cases**:
- Notify Slack when grocery budget exceeded
- Send data to analytics platforms
- Trigger Zapier workflows

**Implementation**:

```python
# Webhook model
class Webhook(Base):
    __tablename__ = 'webhooks'

    id = Column(UUID, primary_key=True)
    user_id = Column(UUID, ForeignKey('users.id'))
    url = Column(String)  # Target URL
    events = Column(ARRAY(String))  # ['grocery.created', 'grocery.deleted']
    secret = Column(String)  # For signature verification
    is_active = Column(Boolean, default=True)

# Webhook delivery service
class WebhookService:
    async def trigger(self, event: str, data: dict):
        # Find all webhooks subscribed to this event
        webhooks = await db.execute(
            "SELECT * FROM webhooks WHERE :event = ANY(events) AND is_active = true",
            {"event": event}
        )

        for webhook in webhooks:
            await self.send_webhook(webhook, event, data)

    async def send_webhook(self, webhook: Webhook, event: str, data: dict):
        payload = {
            "event": event,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }

        # Create signature for security
        signature = hmac.new(
            webhook.secret.encode(),
            json.dumps(payload).encode(),
            hashlib.sha256
        ).hexdigest()

        # Send POST request
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    webhook.url,
                    json=payload,
                    headers={
                        "X-Webhook-Signature": signature,
                        "X-Webhook-Event": event
                    },
                    timeout=5.0
                )

                # Log delivery
                await self.log_delivery(webhook.id, response.status_code)

            except Exception as e:
                # Retry logic
                await self.retry_webhook(webhook, payload)

# Trigger webhooks on events
@router.post("/groceries")
async def create_grocery(data: dict):
    grocery = await service.create_grocery(data)

    # Trigger webhooks
    await webhook_service.trigger("grocery.created", grocery.dict())

    return grocery
```

**Webhook Management Endpoints**:
```python
@router.post("/webhooks")
async def create_webhook(
    url: str,
    events: list[str],
    current_user: User = Depends(get_current_user)
):
    secret = secrets.token_urlsafe(32)

    webhook = await db.insert({
        "user_id": current_user.id,
        "url": url,
        "events": events,
        "secret": secret
    })

    return {"webhook_id": webhook.id, "secret": secret}

@router.delete("/webhooks/{webhook_id}")
async def delete_webhook(webhook_id: str):
    await db.execute("DELETE FROM webhooks WHERE id = ?", webhook_id)
```

**Receiving Webhooks (Example Target)**:
```python
# External service receiving webhooks
@app.post("/receive-webhook")
async def receive_webhook(request: Request):
    payload = await request.json()
    signature = request.headers.get("X-Webhook-Signature")

    # Verify signature
    expected_signature = hmac.new(
        SECRET.encode(),
        json.dumps(payload).encode(),
        hashlib.sha256
    ).hexdigest()

    if signature != expected_signature:
        raise HTTPException(status_code=401, detail="Invalid signature")

    # Process event
    if payload["event"] == "grocery.created":
        print(f"New grocery: {payload['data']['name']}")

    return {"status": "received"}
```

**Success Criteria**:
- Webhooks delivered on events
- Signatures verified for security
- Failed deliveries retried

---

## Phase 7: Storage & Content Delivery (Week 16-17)

### 27. Blob Storage

**Why You Need It**: Store large files (images, receipts, documents) separately from database.

**Use Cases**:
- Upload grocery receipt images
- Product photos
- Nutrition label scans

**Implementation with AWS S3**:

```python
import boto3
from botocore.exceptions import ClientError

class BlobStorageService:
    def __init__(self):
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY,
            aws_secret_access_key=settings.AWS_SECRET_KEY,
            region_name='us-east-1'
        )
        self.bucket = 'grocery-manager-uploads'

    async def upload_file(
        self,
        file_content: bytes,
        file_name: str,
        content_type: str
    ) -> str:
        """Upload file and return public URL"""
        try:
            # Generate unique key
            key = f"receipts/{uuid.uuid4()}/{file_name}"

            # Upload to S3
            self.s3.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=file_content,
                ContentType=content_type,
                ACL='public-read'  # Make publicly accessible
            )

            # Return URL
            url = f"https://{self.bucket}.s3.amazonaws.com/{key}"
            return url

        except ClientError as e:
            raise HTTPException(status_code=500, detail=str(e))

    async def delete_file(self, url: str):
        """Delete file from S3"""
        key = url.split('.amazonaws.com/')[-1]
        self.s3.delete_object(Bucket=self.bucket, Key=key)

# Upload endpoint
@router.post("/groceries/{id}/receipt")
async def upload_receipt(
    id: str,
    file: UploadFile = File(...),
    storage: BlobStorageService = Depends()
):
    # Read file
    content = await file.read()

    # Upload to S3
    url = await storage.upload_file(
        content,
        file.filename,
        file.content_type
    )

    # Save URL to database
    await db.execute(
        "UPDATE groceries SET receipt_url = ? WHERE id = ?",
        (url, id)
    )

    return {"receipt_url": url}
```

**Security - Signed URLs**:
```python
def generate_signed_url(self, key: str, expiration: int = 3600) -> str:
    """Generate temporary signed URL (expires in 1 hour)"""
    url = self.s3.generate_presigned_url(
        'get_object',
        Params={'Bucket': self.bucket, 'Key': key},
        ExpiresIn=expiration
    )
    return url

# Usage for private files
@router.get("/groceries/{id}/receipt")
async def get_receipt(id: str):
    grocery = await db.find_by_id(id)

    # Generate signed URL (temporary access)
    key = grocery.receipt_url.split('.amazonaws.com/')[-1]
    signed_url = storage.generate_signed_url(key)

    return {"url": signed_url}  # Expires in 1 hour
```

**Alternative: Supabase Storage**:
```python
from supabase import create_client

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Upload
supabase.storage.from_('receipts').upload(
    f'user_{user_id}/{file_name}',
    file_content
)

# Get public URL
url = supabase.storage.from_('receipts').get_public_url(f'user_{user_id}/{file_name}')
```

**Success Criteria**:
- Files uploaded to cloud storage
- Database stores URLs only (not files)
- Private files use signed URLs

---

### 28. CDN (Content Delivery Network)

**Why You Need It**:
- Serve static files from servers close to users
- Reduce latency (100ms → 10ms)
- Offload traffic from origin server

**Use Cases**:
- Frontend assets (JS, CSS, images)
- Product images
- Uploaded receipts

**Implementation with CloudFront (AWS CDN)**:

```bash
# 1. Create CloudFront distribution
# Origin: S3 bucket (grocery-manager-uploads)
# Domain: d1234abcd.cloudfront.net

# 2. Update URLs in app
OLD: https://grocery-manager-uploads.s3.amazonaws.com/receipts/abc.jpg
NEW: https://d1234abcd.cloudfront.net/receipts/abc.jpg
```

**Configure Caching**:
```python
# Set cache headers when uploading to S3
self.s3.put_object(
    Bucket=self.bucket,
    Key=key,
    Body=file_content,
    ContentType=content_type,
    CacheControl='max-age=31536000',  # Cache for 1 year
    Metadata={
        'uploaded-by': user_id
    }
)
```

**Cache Invalidation**:
```python
# When file is updated, invalidate CDN cache
import boto3

cloudfront = boto3.client('cloudfront')

def invalidate_cdn_cache(paths: list[str]):
    cloudfront.create_invalidation(
        DistributionId='E1234ABCD',
        InvalidationBatch={
            'Paths': {
                'Quantity': len(paths),
                'Items': paths
            },
            'CallerReference': str(time.time())
        }
    )

# Usage
@router.put("/groceries/{id}/receipt")
async def update_receipt(id: str, file: UploadFile):
    # Delete old file
    old_url = grocery.receipt_url
    await storage.delete_file(old_url)

    # Upload new file
    new_url = await storage.upload_file(...)

    # Invalidate CDN cache
    path = old_url.split('.net')[-1]
    invalidate_cdn_cache([path])

    return {"receipt_url": new_url}
```

**Frontend CDN (for React app)**:
```bash
# Build frontend
cd frontend
npm run build

# Upload to S3
aws s3 sync dist/ s3://grocery-manager-frontend --delete

# CloudFront serves from S3
# Domain: grocery-manager.com → CloudFront → S3
```

**Performance Comparison**:
```
Without CDN:
US → Frankfurt Server → 150ms latency

With CDN:
US → CloudFront (Virginia) → 15ms latency
India → CloudFront (Mumbai) → 20ms latency
Europe → CloudFront (Frankfurt) → 10ms latency
```

**Success Criteria**:
- Static assets served from CDN
- Latency reduced by 80%+
- Cache hit ratio > 90%

---

## Phase 8: Reliability & Advanced Concepts (Week 18-20)

### 29. CAP Theorem

**Why You Need It**: Understand trade-offs in distributed systems.

**CAP Theorem**: In a distributed system, you can only guarantee 2 of 3:
- **C**onsistency: All nodes see same data
- **A**vailability: Every request gets a response
- **P**artition Tolerance: System works despite network failures

**Real-World Example for Grocery Manager**:

#### Scenario 1: Bank Account (Choose CP - Consistency + Partition Tolerance)
```python
# If implementing premium subscriptions with payments
# MUST be consistent (can't charge twice or miss charges)

# Sacrifice availability for consistency
if not can_reach_payment_database():
    raise HTTPException(503, "Payment service temporarily unavailable")
    # Better to fail than to have inconsistent payment state
```

#### Scenario 2: Grocery List (Choose AP - Availability + Partition Tolerance)
```python
# Grocery list can tolerate temporary inconsistency
# User adding items should always work (availability)

# Allow updates even if can't reach main DB
if not can_reach_main_database():
    # Write to local cache, sync later
    await local_cache.add(grocery_item)
    await sync_queue.add(grocery_item)  # Sync when DB available

    return {
        "status": "saved_locally",
        "will_sync": True
    }
```

**Experiment - Eventual Consistency**:
```python
# Multi-region grocery manager
# US database and EU database

class EventuallyConsistentService:
    async def create_grocery(self, data: dict, region: str):
        # Write to local region (fast)
        if region == 'us':
            grocery = await us_db.insert(data)
            # Async replicate to EU (eventual)
            await replication_queue.publish({
                "action": "insert",
                "region": "eu",
                "data": data
            })

        return grocery

    async def list_groceries(self, user_id: str, region: str):
        # Read from local region (might be slightly stale)
        db = us_db if region == 'us' else eu_db
        return await db.find_all(user_id=user_id)

# Trade-off: EU users might see US user's update 1-2 seconds late
# Benefit: Both regions always available, fast local reads/writes
```

**Learning Exercise**:
1. Simulate network partition
2. Test app behavior when database unreachable
3. Implement conflict resolution for concurrent updates

**Success Criteria**: Understand when to choose consistency vs availability for different features.

---

### 30. Idempotency

**Why You Need It**:
- Prevent duplicate operations (double charges, duplicate items)
- Allow safe retries
- Handle network failures gracefully

**Problem**:
```python
# User clicks "Add Grocery" button
# Request sent: POST /groceries
# Network timeout (client doesn't receive response)
# User clicks again (frustrated)
# Result: 2 identical grocery items! 😱
```

**Solution - Idempotency Keys**:

```python
from uuid import UUID

# Client generates unique key per operation
# Frontend
async function createGrocery(data) {
  const idempotencyKey = crypto.randomUUID();

  return fetch('/api/groceries', {
    method: 'POST',
    headers: {
      'Idempotency-Key': idempotencyKey
    },
    body: JSON.stringify(data)
  });
}

# Backend
class IdempotencyService:
    async def check_or_store(
        self,
        key: str,
        user_id: str,
        expiry: int = 86400  # 24 hours
    ) -> Optional[dict]:
        """
        Check if operation already executed.
        Returns cached result if found, None otherwise.
        """
        cache_key = f"idempotency:{user_id}:{key}"

        # Check if key exists
        cached_result = await redis.get(cache_key)
        if cached_result:
            return json.loads(cached_result)  # Already executed

        return None

    async def store_result(self, key: str, user_id: str, result: dict):
        """Store result for future duplicate requests"""
        cache_key = f"idempotency:{user_id}:{key}"
        await redis.setex(cache_key, 86400, json.dumps(result))

@router.post("/groceries")
async def create_grocery(
    data: GroceryCreateSchema,
    idempotency_key: str = Header(None, alias="Idempotency-Key"),
    current_user: User = Depends(get_current_user)
):
    # Require idempotency key for POST requests
    if not idempotency_key:
        raise HTTPException(400, "Idempotency-Key header required")

    # Check if already processed
    cached_result = await idempotency_service.check_or_store(
        idempotency_key,
        current_user.id
    )

    if cached_result:
        # Return cached result (no duplicate insert)
        return JSONResponse(
            content=cached_result,
            headers={"X-Idempotent-Replay": "true"}
        )

    # Process request normally
    grocery = await service.create_grocery(data)
    result = grocery.dict()

    # Store result for future duplicate requests
    await idempotency_service.store_result(
        idempotency_key,
        current_user.id,
        result
    )

    return result
```

**Database-Level Idempotency**:
```python
# Use unique constraints
class Grocery(Base):
    id = Column(UUID, primary_key=True)
    user_id = Column(UUID)
    name = Column(String)
    idempotency_key = Column(String, unique=True)  # Unique constraint

    __table_args__ = (
        UniqueConstraint('user_id', 'idempotency_key', name='uq_user_idempotency'),
    )

# On duplicate key, return existing record
try:
    grocery = await db.insert(data)
except IntegrityError:
    # Already exists - return existing
    grocery = await db.find_one(
        user_id=user_id,
        idempotency_key=idempotency_key
    )
```

**Idempotent DELETE**:
```python
@router.delete("/groceries/{id}")
async def delete_grocery(id: str):
    result = await db.delete(id)

    # Idempotent: Deleting non-existent item returns success
    # (end state is the same - item doesn't exist)
    return Response(status_code=204)
```

**Idempotent UPDATE**:
```python
# Use version numbers or timestamps
class Grocery(Base):
    id = Column(UUID, primary_key=True)
    name = Column(String)
    version = Column(Integer, default=1)  # Optimistic locking

@router.put("/groceries/{id}")
async def update_grocery(
    id: str,
    data: dict,
    current_version: int = Body(...)
):
    # Update only if version matches
    result = await db.execute("""
        UPDATE groceries
        SET name = :name, version = version + 1
        WHERE id = :id AND version = :current_version
        RETURNING *
    """, {
        "name": data["name"],
        "id": id,
        "current_version": current_version
    })

    if not result:
        raise HTTPException(409, "Conflict: Item was modified by another request")

    return result
```

**Success Criteria**:
- Duplicate requests don't create duplicate data
- Failed requests can be safely retried
- Concurrent updates handled correctly

---

## Implementation Tracker

Use this checklist to track your progress:

### Phase 1: Foundation ✅
- [x] Client-Server Architecture (already implemented)
- [ ] IP Address & Networking
- [ ] DNS Configuration
- [ ] HTTP/HTTPS Setup

### Phase 2: API & Security
- [x] APIs (already implemented)
- [x] REST API (already implemented)
- [ ] GraphQL Implementation
- [ ] ⚙️ Authentication & Authorization (Required implementation — not a system design topic)

### Phase 3: Data Layer
- [x] SQL Database (already using)
- [ ] NoSQL Comparison
- [ ] Database Indexing
- [ ] Replication Setup
- [ ] Sharding Strategy
- [ ] Vertical Partitioning

### Phase 4: Performance
- [ ] Redis Caching
- [ ] Denormalization
- [ ] Latency Optimization

### Phase 5: Scalability
- [ ] Vertical Scaling
- [ ] Horizontal Scaling
- [ ] Load Balancers
- [ ] Proxy / Reverse Proxy

### Phase 6: Advanced Patterns
- [ ] Microservices Split
- [ ] Message Queues
- [ ] Rate Limiting
- [ ] API Gateway
- [ ] WebSockets
- [ ] WebHooks

### Phase 7: Storage
- [ ] Blob Storage (S3)
- [ ] CDN Setup

### Phase 8: Reliability
- [ ] CAP Theorem Exercise
- [ ] Idempotency Implementation

---

## Learning Resources

### Books
- "Designing Data-Intensive Applications" by Martin Kleppmann
- "System Design Interview" by Alex Xu

### Practice
- Draw architecture diagrams for each phase
- Monitor metrics (latency, throughput, error rates)
- Load test your application (Apache Bench, Locust)
- Document lessons learned

### Key Metrics to Track
```python
# Add to your app
@router.get("/metrics")
async def get_metrics():
    return {
        "total_requests": request_count,
        "avg_latency_ms": avg_latency,
        "cache_hit_rate": cache_hits / total_cache_requests,
        "database_connections": db_pool.size(),
        "error_rate": errors / total_requests
    }
```

---

## Next Steps

1. **Start with Phase 1**: Get HTTPS working locally
2. **Add Authentication**: This unlocks multi-tenancy
3. **Optimize Database**: Add indexes, then test with 10,000 rows
4. **Add Caching**: Measure improvement
5. **Scale Horizontally**: Deploy multiple instances
6. **Iterate**: Each phase builds on previous ones

Good luck on your system design mastery journey! 🚀