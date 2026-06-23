import os

docs = [
    ("cloud_storage_pricing.md", "# Cloud Storage Pricing\n\nOur cloud storage costs $0.02 per GB per month. Egress is free for the first 100GB, then $0.01 per GB. For billing issues or disputes, please contact human support immediately. Standard support does not cover billing negotiations."),
    ("api_authentication_guide.md", "# API Authentication Guide\n\nTo authenticate with our API, you must include a Bearer token in the Authorization header. `Authorization: Bearer <YOUR_API_KEY>`. If you receive a 401 Unauthorized error, it means your token is missing, expired, or invalid. You can regenerate tokens in the developer dashboard under API Settings."),
    ("database_connection_issues.md", "# Database Connection Issues\n\nIf you are experiencing connection timeouts to the cloud database (Error Code 1004), verify your IP is whitelisted in the firewall rules. Additionally, ensure you are using the correct connection string format: `postgresql://user:password@host:5432/dbname`."),
    ("refund_policy.md", "# Refund Policy\n\nWe do not offer refunds for partial months of service. If you cancel your subscription mid-month, your service will remain active until the end of the billing cycle. For exceptional circumstances, human escalation is required."),
    ("password_reset_guide.md", "# Password Reset Guide\n\nIf you forgot your password, click the 'Forgot Password' link on the login page. An email will be sent with a reset link. If you do not receive the email within 10 minutes, check your spam folder or contact support. Administrators can also trigger a manual reset from the Admin Panel."),
    ("sla_agreement.txt", "Service Level Agreement (SLA)\n\nWe guarantee 99.9% uptime for our core compute services. If uptime falls below 99.9% in a given month, customers are eligible for a 10% service credit. If it falls below 99.0%, a 30% credit is applied. Credits must be requested within 30 days."),
    ("deployment_failures_troubleshooting.md", "# Deployment Failures\n\nIf your CI/CD pipeline fails with 'Insufficient Resources' (Error 507), your environment lacks the CPU/RAM required. You must upgrade your instance type in the project settings. For 'Invalid Configuration' (Error 400), check your `app.yaml` file for syntax errors."),
    ("data_retention_policy.md", "# Data Retention Policy\n\nBy default, backups are retained for 30 days. You can configure custom retention policies up to 365 days. Deleted databases are kept in a soft-delete state for 7 days before permanent purge."),
    ("user_roles_permissions.md", "# Roles and Permissions\n\n- Admin: Full access, can delete projects and manage billing.\n- Editor: Can modify deployments and databases but cannot manage billing.\n- Viewer: Read-only access to logs and metrics."),
    ("network_latency_troubleshooting.txt", "Network Latency Troubleshooting\n\nHigh latency is often caused by routing through sub-optimal regions. Ensure your compute instances are deployed in the same region as your database. For global load balancing, enable CDN features."),
    ("ssl_certificate_management.md", "# SSL Certificate Management\n\nWe provide automated SSL certificates via Let's Encrypt for custom domains. Certificates are renewed automatically 30 days before expiration. If your certificate fails to renew, ensure your DNS A-records are pointing to the correct IP address."),
    ("account_suspension.md", "# Account Suspension\n\nAccounts may be suspended due to failed payments or violation of our Terms of Service. If your account is suspended, all running instances are halted. You must update your payment method to automatically restore service. For ToS violations, human legal escalation is required."),
    ("scaling_instances.md", "# Scaling Compute Instances\n\nAuto-scaling can be enabled in the compute dashboard. You can set minimum and maximum instance counts. Scale-up occurs when CPU utilization exceeds 80% for 5 minutes. Scale-down occurs when CPU is below 20% for 15 minutes."),
    ("exporting_logs.md", "# Exporting Logs\n\nSystem logs can be exported to an external S3 bucket or sent via webhooks. To configure log exporting, go to Project Settings > Monitoring > Log Routing. Exports are processed asynchronously every 5 minutes."),
    ("compliance_hipaa_soc2.md", "# Compliance (HIPAA / SOC2)\n\nOur infrastructure is SOC2 Type II certified. For HIPAA compliance, you must sign a Business Associate Agreement (BAA) and enable 'Dedicated Hardware' mode for all compute and database resources. Contact enterprise sales to sign a BAA.")
]

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    
    os.makedirs(data_dir, exist_ok=True)
    
    print(f"Generating {len(docs)} mock knowledge base documents in {data_dir}...")
    
    for filename, content in docs:
        filepath = os.path.join(data_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
            
    print("Done! You can now run `re-index`.")

if __name__ == "__main__":
    main()
