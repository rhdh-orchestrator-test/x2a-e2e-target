# Analysis: chef-and-ansible

**TLDR**: This repository demonstrates how to use Chef InSpec for compliance testing alongside Ansible deployments. It contains Ansible playbooks that set up an Apache web server with HTTPS and InSpec tests to verify the configuration meets security standards.

## Repository Contents

This repository is not a Chef cookbook requiring migration to Ansible. Instead, it demonstrates the integration of:

1. **Ansible Playbooks**:
   - `website_https.yml`: Sets up an Apache web server with HTTPS using a self-signed certificate
   - `poodle_fix.yml`: Addresses the POODLE vulnerability by restricting SSL protocols

2. **Chef InSpec Tests**:
   - `tests/website_https_verify.rb`: Verifies HTTPS is properly configured
   - `tests/ssh_profile.rb`: Checks SSH configuration for security compliance

## Ansible Playbook Details

### website_https.yml
- Installs Apache 2.4.41
- Installs curl, openssl, and PyOpenSSL
- Creates SSL certificates
- Configures a virtual host for HTTPS
- Deploys a simple "Hello World" website
- Enables SSL module in Apache

### poodle_fix.yml
- Updates SSL configuration to disable vulnerable protocols
- Enables only TLSv1.2
- Restarts Apache and SSH services

## InSpec Test Details

### website_https_verify.rb
- Verifies port 443 is listening
- Checks HTTPS response returns status 200
- Confirms page content contains "Hello, world!"
- Validates SSL3 is disabled
- Ensures TLSv1.2 is enabled

### ssh_profile.rb
- Implements a security control to verify SSH root login is disabled
- Includes detailed rationale and impact information
- Tagged with security requirement references (SRG, CCI, etc.)

## Conclusion

This repository demonstrates how to use Chef InSpec for compliance testing alongside Ansible deployments. It shows how organizations can leverage Ansible for configuration management while using Chef InSpec for security validation and compliance reporting.