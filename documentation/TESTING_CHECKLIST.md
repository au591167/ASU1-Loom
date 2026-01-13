# ASU1-Loom Testing Checklist

## Pre-Testing Setup

### 1. Environment Configuration
- [ ] Copy `.env.example` to `.env`
- [ ] Update `DATABASE_URL` with correct credentials for pandaserver.ddns.net
- [ ] Update `SECRET_KEY` with a secure random key
- [ ] Update `TRAEFIK_EMAIL` with your email
- [ ] Verify all environment variables are set correctly

### 2. Prerequisites Check
- [ ] Docker Desktop is installed and running
- [ ] Docker Compose is available
- [ ] Git is installed
- [ ] Network access to pandaserver.ddns.net:5432

## Critical-Path Testing (Option A)

### Test 1: Database Connection
```bash
# Test PostgreSQL connection
psql -h pandaserver.ddns.net -U loom_user -d loom_db

# Or using Python
python -c "import psycopg2; conn = psycopg2.connect('postgresql://loom_user:PASSWORD@pandaserver.ddns.net:5432/loom_db'); print('✅ Connected'); conn.close()"
```

**Expected Result:** Successful connection to database
- [ ] Connection successful
- [ ] Can list tables
- [ ] Database is accessible

### Test 2: Build Docker Images
```bash
cd Project/ASU1-Loom
docker-compose build
```

**Expected Result:** All images build successfully
- [ ] Backend image builds without errors
- [ ] Frontend image builds without errors
- [ ] No dependency errors

### Test 3: Start Services
```bash
docker-compose up -d
```

**Expected Result:** All services start successfully
- [ ] Traefik starts (port 8080)
- [ ] Backend starts (port 8000)
- [ ] Frontend starts (port 3000)
- [ ] No container crashes

### Test 4: Check Service Health
```bash
# Check running containers
docker-compose ps

# Check logs
docker-compose logs backend
docker-compose logs frontend
docker-compose logs traefik
```

**Expected Result:** All services are healthy
- [ ] All containers show "Up" status
- [ ] No error messages in logs
- [ ] Backend connects to database successfully

### Test 5: Access Frontend
Open browser and navigate to: `http://localhost:3000`

**Expected Result:** Frontend loads successfully
- [ ] Page loads without errors
- [ ] Navigation works (Dashboard, Create, Containers, Settings)
- [ ] Styles are applied correctly
- [ ] No console errors

### Test 6: Access Backend API
Open browser and navigate to: `http://localhost:8000/docs`

**Expected Result:** FastAPI documentation loads
- [ ] Swagger UI is accessible
- [ ] API endpoints are listed
- [ ] Can expand endpoint details

### Test 7: Access GraphQL Playground
Open browser and navigate to: `http://localhost:8000/graphql`

**Expected Result:** GraphQL playground loads
- [ ] GraphQL interface is accessible
- [ ] Schema is loaded
- [ ] Can see available queries and mutations

### Test 8: Test Basic GraphQL Query
In GraphQL playground, run:
```graphql
query {
  containers {
    id
    name
    status
  }
}
```

**Expected Result:** Query executes successfully
- [ ] Query returns data (empty array is OK)
- [ ] No errors in response
- [ ] Response time is reasonable

### Test 9: Access Traefik Dashboard
Open browser and navigate to: `http://localhost:8080`

**Expected Result:** Traefik dashboard loads
- [ ] Dashboard is accessible
- [ ] Shows configured routers
- [ ] Shows services (backend, frontend)

### Test 10: Check Connection Status
In frontend (localhost:3000), go to Settings tab

**Expected Result:** Connection status shows "Connected"
- [ ] API connection is established
- [ ] Status indicator is green
- [ ] No connection errors

## Thorough Testing (Option B)

### Frontend Testing

#### Navigation
- [ ] Dashboard view loads
- [ ] Create New view loads
- [ ] Containers view loads
- [ ] Settings view loads
- [ ] Navigation buttons highlight correctly

#### Dashboard
- [ ] Statistics display correctly
- [ ] Container count shows 0 initially
- [ ] Recent containers section displays
- [ ] Refresh works

#### Create Container Form
- [ ] All form fields are present
- [ ] Validation works (required fields)
- [ ] Pattern validation works (name, subdomain)
- [ ] Number inputs accept valid ranges
- [ ] JSON validation works for environment variables
- [ ] Reset button clears form
- [ ] Submit button is functional

#### Containers List
- [ ] Empty state displays correctly
- [ ] Refresh button works
- [ ] Container cards display properly

#### Settings
- [ ] API endpoint is displayed
- [ ] Connection status updates
- [ ] About information is correct

### Backend Testing

#### GraphQL Queries
Test each query in GraphQL playground:

```graphql
# Get all containers
query {
  containers {
    id
    name
    image
    tag
    status
    subdomain
    port
    createdAt
  }
}

# Get single container
query {
  container(id: "test-id") {
    id
    name
    status
  }
}
```

- [ ] containers query works
- [ ] container query works
- [ ] Proper error handling for invalid IDs

#### GraphQL Mutations
Test each mutation:

```graphql
# Create container
mutation {
  createContainer(input: {
    name: "test-nginx"
    image: "nginx"
    tag: "latest"
    subdomain: "test"
    port: 80
  }) {
    id
    name
    status
  }
}

# Start container
mutation {
  startContainer(id: "container-id") {
    id
    status
  }
}

# Stop container
mutation {
  stopContainer(id: "container-id") {
    id
    status
  }
}

# Delete container
mutation {
  deleteContainer(id: "container-id")
}
```

- [ ] createContainer works
- [ ] startContainer works
- [ ] stopContainer works
- [ ] deleteContainer works
- [ ] Proper error messages for failures

### Docker Integration Testing

#### Container Creation
- [ ] Can create nginx container
- [ ] Can create node container
- [ ] Can create python container
- [ ] Container appears in Docker
- [ ] Container gets correct labels

#### Container Management
- [ ] Can start stopped container
- [ ] Can stop running container
- [ ] Can delete container
- [ ] Status updates correctly
- [ ] Docker SDK integration works

#### Network Configuration
- [ ] Containers join loom_network
- [ ] Containers can communicate
- [ ] Port mapping works correctly

### Traefik Integration Testing

#### Routing
- [ ] Subdomain routing is configured
- [ ] Labels are applied correctly
- [ ] Can access container via subdomain
- [ ] HTTP routing works
- [ ] Dashboard shows routes

### Database Testing

#### Connection
- [ ] Backend connects to PostgreSQL
- [ ] Connection pool works
- [ ] Async operations work

#### CRUD Operations
- [ ] Can create container records
- [ ] Can read container records
- [ ] Can update container records
- [ ] Can delete container records
- [ ] Relationships work correctly

#### Data Persistence
- [ ] Data survives backend restart
- [ ] Transactions work correctly
- [ ] No data corruption

### Error Handling Testing

#### Frontend Errors
- [ ] Invalid form input shows errors
- [ ] API errors display notifications
- [ ] Network errors are handled
- [ ] Loading states work

#### Backend Errors
- [ ] Invalid GraphQL queries return errors
- [ ] Database errors are caught
- [ ] Docker errors are handled
- [ ] Proper HTTP status codes

### Performance Testing

#### Load Testing
- [ ] Can handle multiple containers
- [ ] API response time < 1s
- [ ] Frontend loads quickly
- [ ] No memory leaks

#### Concurrent Operations
- [ ] Multiple container operations work
- [ ] No race conditions
- [ ] Database handles concurrent requests

## Integration Testing

### End-to-End Workflow
1. [ ] Open frontend
2. [ ] Navigate to Create New
3. [ ] Fill in container details
4. [ ] Submit form
5. [ ] Container appears in list
6. [ ] Container is running
7. [ ] Can access via subdomain
8. [ ] Can stop container
9. [ ] Can start container
10. [ ] Can delete container

### Multi-Container Scenario
1. [ ] Create 3 different containers
2. [ ] All containers run simultaneously
3. [ ] Each has unique subdomain
4. [ ] All are accessible
5. [ ] Can manage each independently

## Cleanup

### Stop Services
```bash
docker-compose down
```

- [ ] All containers stop
- [ ] Networks are removed
- [ ] Volumes are preserved (if needed)

### Remove Volumes (if needed)
```bash
docker-compose down -v
```

- [ ] All volumes removed
- [ ] Clean state achieved

## Test Results Summary

### Critical-Path Tests
- Total Tests: 10
- Passed: ___
- Failed: ___
- Skipped: ___

### Thorough Tests
- Total Tests: ___
- Passed: ___
- Failed: ___
- Skipped: ___

### Issues Found
1. 
2. 
3. 

### Recommendations
1. 
2. 
3. 

---

**Testing Date:** ___________  
**Tester:** ___________  
**Environment:** ___________  
**Notes:** ___________
