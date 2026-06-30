# MIGRATION FROM CHEF INSPEC AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to deploy and validate a secure web server configuration. The migration scope is relatively small, focusing on two main components:

1. Ansible playbooks for deploying and configuring Apache web server with HTTPS
2. Chef InSpec tests for validating security compliance

The migration complexity is **LOW** as most of the repository already uses Ansible playbooks. The primary migration task will be converting the Chef InSpec tests to Ansible-native testing solutions. Estimated timeline: **1-2 weeks** for a single developer.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys Apache web server with HTTPS configuration
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL/TLS configuration to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3, enables TLSv1.2 only

- **website_https_verify**:
    - Description: Chef InSpec test that validates HTTPS configuration
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Validates port 443 is listening, HTTPS is working, and secure protocols are enabled

- **ssh_profile**:
    - Description: Chef InSpec test that validates SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: Validates SSH root login is disabled, includes STIG compliance information

- **chef-server-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Automated deployment of Chef infrastructure components

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Simple HTML file used as a test page for the web server

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be targeting on-premises or generic cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic validation
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis of playbooks

- **Test Kitchen**: Replace with Molecule for Ansible-native testing framework
  - Molecule can use Vagrant as a driver similar to Test Kitchen

- **Chef Automate/Infra Server**: If compliance reporting is needed, consider:
  - Ansible Tower/AWX for job scheduling and reporting
  - OpenSCAP for compliance scanning
  - Prometheus/Grafana for metrics and visualization

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening that disables SSLv3 and only enables TLSv1.2
  - Approach: Preserve the same configuration in the Ansible playbooks

- **SSH Security**: The InSpec test validates SSH root login is disabled according to STIG requirements
  - Approach: Create equivalent Ansible assertions or use ansible-lint security rules

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Self-signed SSL certificates generated during deployment
  - Approach: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing
  - Mitigation: Use Ansible's `assert` module with appropriate modules like `uri`, `stat`, and command execution to validate the same conditions

- **Compliance Reporting**: If compliance reporting is a requirement, finding an Ansible-native solution
  - Mitigation: Integrate with OpenSCAP or use Ansible Tower/AWX for reporting

### Migration Order

1. **website_https.yml** and **poodle_fix.yml** (already Ansible, minimal changes needed)
2. **website_https_verify.rb** (convert InSpec tests to Ansible assertions)
3. **ssh_profile.rb** (convert InSpec tests to Ansible assertions)
4. **Chef Server Deployment Scripts** (convert to Ansible roles if Chef infrastructure is still needed)

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation, not for production deployment.
2. The Chef Automate and Chef Infra Server deployment scripts are examples and may not be needed in the final Ansible-only solution.
3. The security compliance requirements (STIG, CCI) mentioned in the InSpec tests need to be maintained in the Ansible solution.
4. Test Kitchen is used primarily for development and testing, not for production deployments.
5. The target environment is Ubuntu 20.04 running on Vagrant VMs.
6. No external data sources or complex dependencies exist beyond what's visible in the repository.
7. The hardcoded credentials in the setup scripts are for demonstration purposes only and would be replaced with secure alternatives in production.