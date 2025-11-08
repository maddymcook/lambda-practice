#!/usr/bin/env python3
"""
Performance comparison script for Docker vs ZIP Lambda endpoints.
Tests both endpoints 500 times each and compares average response times.
"""

import requests
import time
import json
import statistics
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from collections import Counter
import argparse

# Configuration
DOCKER_ENDPOINT = "https://api.follicle-force-3000.com/process-profile-docker"
ZIP_ENDPOINT = "https://api.follicle-force-3000.com/process-profile"

TEST_PAYLOAD = {
    "name": "John Doe",
    "email": "john@example.com",
    "age": 30,
    "interests": ["coding", "music", "travel"]
}

HEADERS = {
    "Content-Type": "application/json"
}

def make_request(endpoint, payload, headers):
    """Make a single request and return the response time in milliseconds."""
    start_time = time.time()
    error_details = None
    response_text = None

    try:
        response = requests.post(endpoint, json=payload, headers=headers, timeout=30)
        end_time = time.time()
        response_time_ms = (end_time - start_time) * 1000

        # Get response text for error analysis
        try:
            response_text = response.text
        except:
            response_text = "Unable to read response text"

        return {
            'response_time_ms': response_time_ms,
            'status_code': response.status_code,
            'success': response.status_code == 200,
            'response_text': response_text if response.status_code != 200 else None,
            'error': None,
            'error_type': None
        }
    except requests.exceptions.Timeout as e:
        end_time = time.time()
        response_time_ms = (end_time - start_time) * 1000
        error_details = f"Timeout after 30s: {str(e)}"
        print(f"⚠️  Timeout error: {error_details}", file=sys.stderr)
        return {
            'response_time_ms': response_time_ms,
            'status_code': None,
            'success': False,
            'response_text': None,
            'error': error_details,
            'error_type': 'timeout'
        }
    except requests.exceptions.ConnectionError as e:
        end_time = time.time()
        response_time_ms = (end_time - start_time) * 1000
        error_details = f"Connection error: {str(e)}"
        print(f"⚠️  Connection error: {error_details}", file=sys.stderr)
        return {
            'response_time_ms': response_time_ms,
            'status_code': None,
            'success': False,
            'response_text': None,
            'error': error_details,
            'error_type': 'connection'
        }
    except requests.exceptions.RequestException as e:
        end_time = time.time()
        response_time_ms = (end_time - start_time) * 1000
        error_details = f"Request error: {str(e)}"
        print(f"⚠️  Request error: {error_details}", file=sys.stderr)
        return {
            'response_time_ms': response_time_ms,
            'status_code': None,
            'success': False,
            'response_text': None,
            'error': error_details,
            'error_type': 'request'
        }
    except Exception as e:
        end_time = time.time()
        response_time_ms = (end_time - start_time) * 1000
        error_details = f"Unexpected error: {str(e)}"
        print(f"⚠️  Unexpected error: {error_details}", file=sys.stderr)
        return {
            'response_time_ms': response_time_ms,
            'status_code': None,
            'success': False,
            'response_text': None,
            'error': error_details,
            'error_type': 'unexpected'
        }

def test_endpoint(endpoint_name, endpoint_url, num_requests=500, max_workers=10):
    """Test an endpoint with multiple concurrent requests."""
    print(f"\n🚀 Testing {endpoint_name} endpoint...")
    print(f"URL: {endpoint_url}")
    print(f"Requests: {num_requests}, Max Workers: {max_workers}")
    print("-" * 60)

    results = []
    successful_requests = 0
    failed_requests = 0

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all requests
        futures = [
            executor.submit(make_request, endpoint_url, TEST_PAYLOAD, HEADERS)
            for _ in range(num_requests)
        ]

        # Collect results with progress indication
        for i, future in enumerate(as_completed(futures), 1):
            result = future.result()
            results.append(result)

            if result['success']:
                successful_requests += 1
            else:
                failed_requests += 1

            # Show progress every 50 requests
            if i % 50 == 0 or i == num_requests:
                print(f"Progress: {i}/{num_requests} requests completed")

    # Calculate statistics for successful requests only
    successful_times = [r['response_time_ms'] for r in results if r['success']]

    # Collect error statistics
    failed_results = [r for r in results if not r['success']]
    error_types = Counter([r['error_type'] for r in failed_results if r['error_type']])
    status_codes = Counter([r['status_code'] for r in results if r['status_code'] is not None])

    # Get sample errors for analysis
    sample_errors = []
    for error_type in error_types.keys():
        sample = next((r for r in failed_results if r['error_type'] == error_type), None)
        if sample:
            sample_errors.append({
                'error_type': error_type,
                'error_message': sample['error'],
                'response_text': sample.get('response_text', 'No response text')
            })

    if successful_times:
        stats = {
            'endpoint_name': endpoint_name,
            'total_requests': num_requests,
            'successful_requests': successful_requests,
            'failed_requests': failed_requests,
            'success_rate': (successful_requests / num_requests) * 100,
            'avg_response_time_ms': statistics.mean(successful_times),
            'median_response_time_ms': statistics.median(successful_times),
            'min_response_time_ms': min(successful_times),
            'max_response_time_ms': max(successful_times),
            'std_dev_ms': statistics.stdev(successful_times) if len(successful_times) > 1 else 0,
            'p95_response_time_ms': statistics.quantiles(successful_times, n=20)[18] if len(successful_times) >= 20 else max(successful_times),
            'p99_response_time_ms': statistics.quantiles(successful_times, n=100)[98] if len(successful_times) >= 100 else max(successful_times),
            'error_breakdown': dict(error_types),
            'status_code_breakdown': dict(status_codes),
            'sample_errors': sample_errors
        }
    else:
        stats = {
            'endpoint_name': endpoint_name,
            'total_requests': num_requests,
            'successful_requests': 0,
            'failed_requests': failed_requests,
            'success_rate': 0,
            'avg_response_time_ms': 0,
            'median_response_time_ms': 0,
            'min_response_time_ms': 0,
            'max_response_time_ms': 0,
            'std_dev_ms': 0,
            'p95_response_time_ms': 0,
            'p99_response_time_ms': 0,
            'error_breakdown': dict(error_types),
            'status_code_breakdown': dict(status_codes),
            'sample_errors': sample_errors
        }

    return stats, results

def print_results(stats):
    """Print formatted results for an endpoint."""
    print(f"\n📊 Results for {stats['endpoint_name']}:")
    print(f"  Success Rate: {stats['success_rate']:.1f}% ({stats['successful_requests']}/{stats['total_requests']})")

    if stats['successful_requests'] > 0:
        print(f"  Average Response Time: {stats['avg_response_time_ms']:.2f} ms")
        print(f"  Median Response Time: {stats['median_response_time_ms']:.2f} ms")
        print(f"  Min Response Time: {stats['min_response_time_ms']:.2f} ms")
        print(f"  Max Response Time: {stats['max_response_time_ms']:.2f} ms")
        print(f"  Standard Deviation: {stats['std_dev_ms']:.2f} ms")
        print(f"  95th Percentile: {stats['p95_response_time_ms']:.2f} ms")
        print(f"  99th Percentile: {stats['p99_response_time_ms']:.2f} ms")

    # Print error breakdown if there were failures
    if stats['failed_requests'] > 0:
        print(f"\n  ❌ Error Analysis ({stats['failed_requests']} failures):")

        # Error type breakdown
        if stats['error_breakdown']:
            print(f"    Error Types:")
            for error_type, count in stats['error_breakdown'].items():
                percentage = (count / stats['failed_requests']) * 100
                print(f"      - {error_type}: {count} ({percentage:.1f}%)")

        # Status code breakdown
        if stats['status_code_breakdown']:
            print(f"    Status Codes:")
            for status_code, count in stats['status_code_breakdown'].items():
                percentage = (count / stats['total_requests']) * 100
                print(f"      - {status_code}: {count} ({percentage:.1f}%)")

        # Sample errors
        if stats['sample_errors']:
            print(f"    Sample Error Messages:")
            for i, error_sample in enumerate(stats['sample_errors'][:3], 1):  # Show up to 3 samples
                print(f"      {i}. {error_sample['error_type']}: {error_sample['error_message'][:100]}...")
                if error_sample['response_text'] and error_sample['response_text'] != 'No response text':
                    print(f"         Response: {error_sample['response_text'][:100]}...")

        # Write detailed errors to stderr for debugging
        print(f"\n  💾 Detailed error logs written to stderr", file=sys.stderr)


def print_comparison(docker_stats, zip_stats):
    """Print comparison between Docker and ZIP endpoints."""
    print("\n" + "=" * 60)
    print("🏁 PERFORMANCE COMPARISON")
    print("=" * 60)

    if docker_stats['successful_requests'] > 0 and zip_stats['successful_requests'] > 0:
        docker_avg = docker_stats['avg_response_time_ms']
        docker_std = docker_stats['std_dev_ms']
        zip_avg = zip_stats['avg_response_time_ms']
        zip_std = zip_stats['std_dev_ms']

        if docker_avg < zip_avg:
            faster = "Docker"
            slower = "ZIP"
            improvement = ((zip_avg - docker_avg) / zip_avg) * 100
        else:
            faster = "ZIP"
            slower = "Docker"
            improvement = ((docker_avg - zip_avg) / docker_avg) * 100

        print(f"🏆 Winner: {faster} endpoint")
        print(f"📈 Performance improvement: {improvement:.1f}% faster")
        print(f"⏱️  Docker average: {docker_avg:.2f} ms (±{docker_std:.2f} ms)")
        print(f"⏱️  ZIP average: {zip_avg:.2f} ms (±{zip_std:.2f} ms)")
        print(f"📊 Difference: {abs(docker_avg - zip_avg):.2f} ms")

        # Calculate standard error for comparison
        docker_se = docker_std / (docker_stats['successful_requests'] ** 0.5)
        zip_se = zip_std / (zip_stats['successful_requests'] ** 0.5)
        print(f"📏 Standard Error - Docker: ±{docker_se:.2f} ms, ZIP: ±{zip_se:.2f} ms")
    else:
        print("⚠️  Cannot compare - one or both endpoints had no successful requests")

def save_results_to_file(docker_stats, zip_stats, docker_results, zip_results):
    """Save detailed results to JSON files."""
    timestamp = time.strftime("%Y%m%d_%H%M%S")

    # Save summary
    summary = {
        'test_timestamp': timestamp,
        'test_payload': TEST_PAYLOAD,
        'docker_stats': docker_stats,
        'zip_stats': zip_stats
    }

    with open(f'performance_test_summary_{timestamp}.json', 'w') as f:
        json.dump(summary, f, indent=2)

    # Save detailed results
    detailed = {
        'test_timestamp': timestamp,
        'docker_results': docker_results,
        'zip_results': zip_results
    }

    with open(f'performance_test_detailed_{timestamp}.json', 'w') as f:
        json.dump(detailed, f, indent=2)

    print(f"\n💾 Results saved to:")
    print(f"  - performance_test_summary_{timestamp}.json")
    print(f"  - performance_test_detailed_{timestamp}.json")

def main():
    parser = argparse.ArgumentParser(description='Performance test for Lambda endpoints')
    parser.add_argument('--requests', '-r', type=int, default=500, help='Number of requests per endpoint (default: 500)')
    parser.add_argument('--workers', '-w', type=int, default=10, help='Max concurrent workers (default: 10)')
    parser.add_argument('--docker-only', action='store_true', help='Test only Docker endpoint')
    parser.add_argument('--zip-only', action='store_true', help='Test only ZIP endpoint')

    args = parser.parse_args()

    print("🔥 Lambda Performance Test")
    print("=" * 60)
    print(f"Test Configuration:")
    print(f"  Requests per endpoint: {args.requests}")
    print(f"  Max concurrent workers: {args.workers}")
    print(f"  Test payload: {json.dumps(TEST_PAYLOAD, indent=2)}")

    docker_stats = None
    zip_stats = None
    docker_results = []
    zip_results = []

    if not args.zip_only:
        # Test Docker endpoint
        docker_stats, docker_results = test_endpoint(
            "Docker", DOCKER_ENDPOINT, args.requests, args.workers
        )
        print_results(docker_stats)

    if not args.docker_only:
        # Test ZIP endpoint
        zip_stats, zip_results = test_endpoint(
            "ZIP", ZIP_ENDPOINT, args.requests, args.workers
        )
        print_results(zip_stats)

    # Compare results if both were tested
    if docker_stats and zip_stats:
        print_comparison(docker_stats, zip_stats)
        save_results_to_file(docker_stats, zip_stats, docker_results, zip_results)
    elif docker_stats:
        save_results_to_file(docker_stats, {}, docker_results, [])
    elif zip_stats:
        save_results_to_file({}, zip_stats, [], zip_results)

if __name__ == "__main__":
    main()
