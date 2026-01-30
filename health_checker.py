# health_checker.py - FINAL VERSION

#!/usr/bin/env python3
"""
AWS Resource Health Checker
===========================
A command-line tool to monitor AWS infrastructure health.
Checks EC2 instance status and CloudWatch alarms.

Author: Marvelous Olabinjo
GitHub: https://github.com/MarvelOlas/aws-health-checker
"""

import boto3
import json
import argparse
from datetime import datetime
from botocore.exceptions import ClientError, NoCredentialsError


def check_ec2_instances(region):
    """
    Check the status of all EC2 instances in a region.
    
    Args:
        region (str): AWS region name
    
    Returns:
        list: List of instance dictionaries with id, type, state, name
    """
    print(f"\n{'='*50}")
    print("EC2 INSTANCE STATUS")
    print(f"{'='*50}")
    
    try:
        ec2 = boto3.client('ec2', region_name=region)
        response = ec2.describe_instances()
    except NoCredentialsError:
        print("❌ Error: AWS credentials not configured")
        print("   Run 'aws configure' to set up credentials")
        return []
    except ClientError as e:
        print(f"❌ Error: {e.response['Error']['Message']}")
        return []
    
    instances = []
    
    for reservation in response['Reservations']:
        for instance in reservation['Instances']:
            instance_info = {
                'instance_id': instance['InstanceId'],
                'instance_type': instance['InstanceType'],
                'state': instance['State']['Name'],
                'name': 'Unnamed'
            }
            
            # Get Name tag if exists
            for tag in instance.get('Tags', []):
                if tag['Key'] == 'Name':
                    instance_info['name'] = tag['Value']
                    break
            
            instances.append(instance_info)
            
            # Display with status indicator
            status_icons = {
                'running': '✅',
                'stopped': '🛑',
                'pending': '⏳',
                'stopping': '⏳',
                'terminated': '💀'
            }
            status = status_icons.get(instance_info['state'], '⚠️')
            
            print(f"{status} {instance_info['name']} ({instance_info['instance_id']})")
            print(f"   Type: {instance_info['instance_type']}, State: {instance_info['state']}")
    
    if not instances:
        print("ℹ️  No EC2 instances found in this region.")
    
    return instances


def check_cloudwatch_alarms(region):
    """
    Check the status of all CloudWatch alarms in a region.
    
    Args:
        region (str): AWS region name
    
    Returns:
        list: List of alarm dictionaries with name, state, metric
    """
    print(f"\n{'='*50}")
    print("CLOUDWATCH ALARM STATUS")
    print(f"{'='*50}")
    
    try:
        cloudwatch = boto3.client('cloudwatch', region_name=region)
        response = cloudwatch.describe_alarms()
    except NoCredentialsError:
        print("❌ Error: AWS credentials not configured")
        return []
    except ClientError as e:
        print(f"❌ Error: {e.response['Error']['Message']}")
        return []
    
    alarms = []
    
    for alarm in response['MetricAlarms']:
        alarm_info = {
            'name': alarm['AlarmName'],
            'state': alarm['StateValue'],
            'metric': alarm['MetricName'],
            'description': alarm.get('AlarmDescription', 'No description')
        }
        alarms.append(alarm_info)
        
        status_icons = {
            'OK': '✅',
            'ALARM': '🚨',
            'INSUFFICIENT_DATA': '⚠️'
        }
        status = status_icons.get(alarm_info['state'], '❓')
        
        print(f"{status} {alarm_info['name']}")
        print(f"   State: {alarm_info['state']}, Metric: {alarm_info['metric']}")
    
    if not alarms:
        print("ℹ️  No CloudWatch alarms configured in this region.")
    
    return alarms


def generate_summary(instances, alarms):
    """
    Generate and display a summary of the health check.
    
    Args:
        instances (list): List of EC2 instance data
        alarms (list): List of CloudWatch alarm data
    
    Returns:
        dict: Summary statistics
    """
    print(f"\n{'='*50}")
    print("SUMMARY")
    print(f"{'='*50}")
    
    # Calculate instance statistics
    total_instances = len(instances)
    running = sum(1 for i in instances if i['state'] == 'running')
    stopped = sum(1 for i in instances if i['state'] == 'stopped')
    other = total_instances - running - stopped
    
    # Calculate alarm statistics
    total_alarms = len(alarms)
    alarming = sum(1 for a in alarms if a['state'] == 'ALARM')
    ok_alarms = sum(1 for a in alarms if a['state'] == 'OK')
    
    # Display summary
    print(f"\n📊 EC2 Instances:")
    print(f"   Total: {total_instances}")
    print(f"   Running: {running}")
    print(f"   Stopped: {stopped}")
    if other > 0:
        print(f"   Other: {other}")
    
    print(f"\n📊 CloudWatch Alarms:")
    print(f"   Total: {total_alarms}")
    print(f"   OK: {ok_alarms}")
    print(f"   In Alarm: {alarming}")
    
    # Overall health assessment
    print(f"\n{'='*50}")
    if alarming > 0:
        print("⚠️  ATTENTION: There are active alarms that need investigation!")
    elif running == total_instances and total_instances > 0:
        print("✅ ALL SYSTEMS HEALTHY")
    elif total_instances == 0 and total_alarms == 0:
        print("ℹ️  No resources found to monitor")
    else:
        print("⚠️  Some instances are not running")
    print(f"{'='*50}")
    
    return {
        'total_instances': total_instances,
        'running_instances': running,
        'stopped_instances': stopped,
        'total_alarms': total_alarms,
        'active_alarms': alarming
    }


def save_report(filename, region, instances, alarms, summary):
    """
    Save the health report to a JSON file.
    
    Args:
        filename (str): Output filename
        region (str): AWS region
        instances (list): Instance data
        alarms (list): Alarm data
        summary (dict): Summary statistics
    """
    report = {
        'report_metadata': {
            'generated_at': datetime.now().isoformat(),
            'region': region,
            'tool': 'AWS Health Checker',
            'author': 'Marvelous Olabinjo'
        },
        'instances': instances,
        'alarms': alarms,
        'summary': summary
    }
    
    with open(filename, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Report saved to: {filename}")


def main():
    """
    Main function - entry point for the health checker.
    """
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='AWS Resource Health Checker - Monitor your AWS infrastructure',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python health_checker.py                    # Check eu-west-1 (default)
  python health_checker.py --region us-east-1 # Check specific region
  python health_checker.py --output report.json  # Save to file
        """
    )
    parser.add_argument(
        '--region',
        default='eu-west-1',
        help='AWS region to check (default: eu-west-1)'
    )
    parser.add_argument(
        '--output',
        metavar='FILE',
        help='Save report to JSON file'
    )
    
    args = parser.parse_args()
    
    # Display header
    print("\n" + "=" * 50)
    print("🔍 AWS HEALTH CHECKER")
    print("=" * 50)
    print(f"📅 Report Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🌍 Region: {args.region}")
    
    # Run health checks
    instances = check_ec2_instances(args.region)
    alarms = check_cloudwatch_alarms(args.region)
    
    # Generate summary
    summary = generate_summary(instances, alarms)
    
    # Save to file if requested
    if args.output:
        save_report(args.output, args.region, instances, alarms, summary)
    
    print("\n✅ Health check complete!\n")


if __name__ == "__main__":
    main()
