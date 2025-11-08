```markdown
# Lambda Function Demo

A simple AWS Lambda function that processes multiple input values and performs calculations.

## Prerequisites

- Docker installed on your machine
- Python 3.11+ (for local development)
- AWS CLI configured (for deployed testing)

## Project Structure

```
.
├── Dockerfile
├── lambda_function.py
├── requirements.txt (optional)
└── README.md
```

## Local Development

### 1. Build the Docker Image

```bash
docker build -t my-lambda-function .
```

### 2. Run the Container Locally

```bash
docker run -p 9000:8080 my-lambda-function
```

This starts the Lambda Runtime Interface Emulator on port 9000.

### 3. Test the Function

Open a new terminal and test with curl:

**User Profile Example:**
```bash
curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" \
  -d '{"body": "{\"name\": \"john doe\", \"email\": \"john@example.com\", \"age\": 28, \"interests\": [\"coding\", \"music\"]}"}'

curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" \
  -d '{"body": "{\"name\": \"jane smith\", \"email\": \"\", \"age\": 16, \"interests\": [\"gaming\"]}"}'
```

## Testing via Custom Domain (Recommended)

The easiest way to test the API is using the custom domain. Two endpoints are available:

### Standard Endpoint

```bash
curl -X POST https://api.follicle-force-3000.com/process-profile \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "age": 30,
    "interests": ["coding", "music", "travel"]
  }'
```

### Docker-based Endpoint

```bash
curl -X POST https://5bxgleksjh.execute-api.us-west-2.amazonaws.com/scoreProfileDocker
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "age": 30,
    "interests": ["coding", "music", "travel"]
  }'
```

**Expected Response (both endpoints):**
```json
{
  "message": "Profile processed successfully",
  "original_input": {
    "name": "John Doe",
    "email": "john@example.com",
    "age": 30,
    "interests": ["coding", "music", "travel"]
  },
  "processed_profile": {
    "full_name": "John Doe",
    "email_domain": "example.com",
    "age_group": "adult",
    "interest_count": 3,
    "profile_score": 100,
    "created_at": "2025-10-28T14:49:51.038237"
  }
}
```

### Test Different Scenarios

You can use either endpoint (`/process-profile` or `/process-profile-docker`) for these tests:

**Valid adult user:**
```bash
curl -X POST https://api.follicle-force-3000.com/process-profile-docker \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Alice Johnson",
    "email": "alice@company.com",
    "age": 25,
    "interests": ["reading", "hiking", "photography"]
  }'
```

**Minor user:**
```bash
curl -X POST https://api.follicle-force-3000.com/process-profile-docker \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Charlie Brown",
    "email": "charlie@school.edu",
    "age": 16,
    "interests": ["gaming", "music"]
  }'
```

**Senior user:**
```bash
curl -X POST https://api.follicle-force-3000.com/process-profile-docker \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Robert Wilson",
    "email": "bob@retirement.com",
    "age": 70,
    "interests": ["gardening", "reading"]
  }'
```

**Invalid email test:**
```bash
curl -X POST https://api.follicle-force-3000.com/process-profile-docker \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Bob Smith",
    "email": "invalid-email",
    "age": 45,
    "interests": ["sports"]
  }'
```

**Empty interests:**
```bash
curl -X POST https://api.follicle-force-3000.com/process-profile-docker \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Jane Doe",
    "email": "jane@example.com",
    "age": 35,
    "interests": []
  }'
```

**Minimal data:**
```bash
curl -X POST https://api.follicle-force-3000.com/process-profile-docker \
  -H "Content-Type: application/json" \
  -d '{
    "name": "",
    "email": "",
    "age": 0,
    "interests": []
  }'
```

## Testing via API Gateway (Alternative)

You can also test using the direct API Gateway URL:

### Basic API Gateway Test

```bash
curl -X POST https://3curjopzvj.execute-api.us-west-2.amazonaws.com/process-profile \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "age": 30,
    "interests": ["coding", "music", "travel"]
  }'
```

## Testing Deployed Lambda Function (Direct)

Once your function is deployed to AWS, you can also test it directly using the AWS CLI:

### Prerequisites for Deployed Testing
- AWS CLI installed and configured
- Appropriate IAM permissions to invoke Lambda functions
- Function deployed with name `profileScorer` (or update the function name below)

### 1. Direct Lambda Invocation

```bash
aws lambda invoke \
  --function-name profileScorer \
  --payload $(echo '{"body": "{\"name\":\"John Doe\",\"email\":\"john@example.com\",\"age\":30,\"interests\":[\"coding\",\"music\"]}"}' | base64) \
  response.json
```

### 2. Alternative: Using a Payload File

Create a file `test-payload.json`:
```json
{
  "body": "{\"name\":\"John Doe\",\"email\":\"john@example.com\",\"age\":30,\"interests\":[\"coding\",\"music\"]}"
}
```

Then invoke:
```bash
aws lambda invoke \
  --function-name profileScorer \
  --payload fileb://test-payload.json \
  response.json
```

### 3. Check the Response

View the response:
```bash
cat response.json
```

### 4. Region Configuration

If your function is in a specific region, specify it:
```bash
aws lambda invoke \
  --region us-west-2 \
  --function-name profileScorer \
  --payload fileb://test-payload.json \
  response.json
```

Or set the default region:
```bash
export AWS_DEFAULT_REGION=us-west-2
```

## Understanding the Response

The API returns a JSON object with three main sections:

- **message**: Status message indicating success or failure
- **original_input**: The exact data you sent to the API
- **processed_profile**: The calculated results including:
  - `full_name`: Properly capitalized name
  - `email_domain`: Domain extracted from email address
  - `age_group`: "minor" (< 18), "adult" (18-64), or "senior" (65+)
  - `interest_count`: Number of interests provided
  - `profile_score`: Score out of 100 based on data completeness
  - `created_at`: Timestamp when the profile was processed

## Available Endpoints

The API provides two endpoints with identical functionality:

- **`/process-profile`**: Standard Lambda function endpoint
- **`/process-profile-docker`**: Docker-based Lambda function endpoint

Both endpoints accept the same input format and return identical responses. Choose either based on your preference or testing needs.

## Stopping the Container

Press `Ctrl+C` in the terminal where the container is running, or:

```bash
docker ps
docker stop <container_id>
```

## Rebuilding After Changes

If you modify the code:

1. Stop the running container
2. Rebuild the image: `docker build -t my-lambda-function .`
3. Run again: `docker run -p 9000:8080 my-lambda-function`

## Troubleshooting

- **Port already in use**: Change the port mapping: `docker run -p 9001:8080 my-lambda-function`
- **Function not found**: Ensure your Python file is named `lambda_function.py` and contains `lambda_handler`
- **JSON parsing errors**: Make sure to properly escape quotes in your test JSON
- **ResourceNotFoundException**: Check that the function name and region are correct
- **Invalid base64 error**: Use `fileb://` prefix for payload files or ensure proper base64 encoding
- **API Gateway 404**: Verify the endpoint URL and path are correct
- **CORS issues**: If testing from a browser, ensure CORS is configured on the API Gateway
- **Domain not resolving**: Ensure DNS is properly configured for the custom domain

## Performance Testing

Use the included performance test script to compare Docker vs ZIP Lambda endpoints:

```bash
# Install dependencies
pip install requests

# Run performance test (500 requests to each endpoint)
python performance_test.py

# Run with custom parameters
python performance_test.py --requests 1000 --workers 20

# Test only Docker endpoint
python performance_test.py --docker-only

# Test only ZIP endpoint
python performance_test.py --zip-only
```

The script will:
- Send 500 concurrent requests to each endpoint
- Measure response times and calculate statistics
- Show error breakdown with stderr logging
- Generate JSON reports with detailed results
- Compare performance between Docker and ZIP deployments

**Sample Output:**
```
🚀 Testing Docker endpoint...
Progress: 500/500 requests completed

📊 Results for Docker:
  Success Rate: 100.0% (500/500)
  Average Response Time: 245.67 ms
  95th Percentile: 298.45 ms
  99th Percentile: 345.12 ms
```

## Deployment

To deploy to AWS Lambda:
1. Push the image to Amazon ECR
2. Create a Lambda function using the container image
3. Configure triggers (API Gateway, etc.)
4. Set up custom domain mapping (optional)
` ` `

**Key changes made:**
1. **Added Docker endpoint section** with both `/process-profile` and `/process-profile-docker` options
2. **Updated test scenarios** to use the new Docker endpoint
3. **Added "Available Endpoints" section** explaining both options
4. **Updated expected response** with the new timestamp format
5. **Clarified that both endpoints are functionally identical**
