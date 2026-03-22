# MEMORY_INTEGRATION_GUIDE

## Overview
This document provides comprehensive guidance on integrating the persistent memory system into the Finance GPT Agent.

## 1. Setup Instructions
### Prerequisites
- Ensure that you have Docker installed.
- A relational database is required (e.g., PostgreSQL).

### Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/2343431/finance-gpt-agent.git
   cd finance-gpt-agent
   ```
2. Configure your database settings in the `config.json` file.
3. Build your Docker image:
   ```bash
   docker build -t finance-gpt-agent .
   ```
4. Run your Docker container:
   ```bash
   docker run -d -p 8000:8000 finance-gpt-agent
   ```

## 2. Database Schema
The schema for the persistent memory system consists of the following tables:

### Users Table
| Column Name | Data Type | Description |
|-------------|-----------|-------------|
| id          | INT       | Primary Key |
| username    | VARCHAR   | User's name |
| password    | VARCHAR   | Hashed password |

### Transactions Table
| Column Name   | Data Type | Description                           |
|---------------|-----------|---------------------------------------|
| id            | INT       | Primary Key                           |
| user_id       | INT       | Foreign Key referencing Users(id)     |
| amount        | DECIMAL   | Transaction amount                     |
| transaction_date | TIMESTAMP | Date and time of the transaction   |

## 3. Docker Deployment
To deploy the service using Docker:
- Make sure Docker is running.
- Follow the setup instructions above to build and run the container.
- Access the application at `http://localhost:8000`.

## 4. API Usage Examples
### Fetch User Transactions
```bash
curl -X GET http://localhost:8000/api/transactions?user_id=1
```
### Create a new Transaction
```bash
curl -X POST http://localhost:8000/api/transactions \
-H "Content-Type: application/json" \
-d '{"user_id":1,"amount":100.00}'
```

## 5. Architecture Overview
The architecture of the Finance GPT Agent integrates:
- **Frontend**: User interface built with React.
- **Backend**: RESTful API built with Node.js.
- **Database**: PostgreSQL for persistent memory storage.
- **Docker**: For containerization and easy deployment.