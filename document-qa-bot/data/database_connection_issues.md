# Database Connection Issues

If you are experiencing connection timeouts to the cloud database (Error Code 1004), verify your IP is whitelisted in the firewall rules. Additionally, ensure you are using the correct connection string format: `postgresql://user:password@host:5432/dbname`.