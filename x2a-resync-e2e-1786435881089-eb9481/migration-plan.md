# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec tests. The migration scope is relatively small, focusing on:

1. Converting Chef Automate/Infra Server deployment scripts to Ansible playbooks
2. Preserving existing Ansible playbooks while standardizing their structure
3. Maintaining Chef InSpec tests for compliance validation
4. Creating a unified Ansible-based workflow for both infrastructure deployment and compliance testing

**Estimated Timeline**: 1-2 weeks for a small team (1-2 engineers)
**Complexity**: Low to Medium - The repository contains simple deployment scripts and basic Ansible playbooks

## Module Migration Plan

This repository contains both Ansible playbooks and Chef deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration, including self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL vulnerabilities in Apache by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **chef-automate-deploy**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server on a VM
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

- **chef-server-deploy**:
    - Description: Bash script that deploys Chef Infra Server (without Automate) on a VM
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/tests/website_https_verify.rb`: Chef InSpec test file for validating HTTPS configuration
- `chef-and-ansible/index.html`: Likely a sample HTML file for testing web server deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in Test Kitchen configuration)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with on-premises focus

## Migration Approach

### Key Dependencies to Address

- **Chef Automate CLI**: Replace with Ansible roles for configuration management
- **Chef Server CLI**: Replace with Ansible roles for configuration management
- **Test Kitchen with Ansible**: Migrate to Ansible Molecule for testing
- **Chef InSpec**: Maintain as a compliance testing tool, integrated with Ansible workflows

### Security Considerations

- **SSL/TLS Configuration**: The playbooks configure Apache with TLS 1.2 and disable older protocols
  - Migration approach: Preserve this security hardening in Ansible roles
  - Consider updating to include TLS 1.3 support

- **Self-signed Certificates**: The playbooks generate self-signed certificates
  - Migration approach: Create an Ansible role for certificate management with options for both self-signed and proper CA-signed certificates

- **Hardcoded Credentials**: The Chef deployment scripts contain hardcoded credentials
  - Migration approach: Replace with Ansible Vault for secure credential storage
  - Document the count and type of credentials detected per module:
    - chef-automate-deploy: 4 credentials (username, password, organization name, email)
    - chef-server-deploy: 4 credentials (username, password, organization name, email)

### Technical Challenges

- **Chef Automate Deployment**: Converting the Chef Automate deployment script to Ansible
  - Mitigation: Create an Ansible role that installs and configures Chef Automate using the official API
  - Alternative: If Chef Automate is being used primarily for compliance, consider replacing it with pure Ansible + InSpec solution

- **InSpec Integration**: Maintaining InSpec tests while moving to Ansible
  - Mitigation: Use Ansible's `community.general.inspec` module to run InSpec tests as part of Ansible playbooks

### Migration Order

1. **website_https and poodle_fix playbooks** (low risk, already in Ansible)
   - Standardize structure following Ansible best practices
   - Convert to roles for better reusability
   - Update Test Kitchen configuration to use Molecule

2. **Chef deployment scripts** (moderate complexity)
   - Create Ansible roles to replace the bash scripts
   - Implement Ansible Vault for credential storage
   - Add idempotency checks to ensure safe re-runs

3. **Testing Framework** (low complexity)
   - Migrate from Test Kitchen to Molecule for testing
   - Maintain InSpec tests but integrate them with Ansible workflow

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployments (based on README.md content)
2. The Chef Automate and Chef Server deployments are intended for on-premises use
3. The hardcoded credentials in the deployment scripts are examples and not actual production credentials
4. The InSpec tests are intended to be run as part of a CI/CD pipeline
5. The target audience is familiar with both Chef and Ansible technologies
6. The Apache configuration is a simple example and not a complete production configuration
7. The self-signed certificates are for demonstration purposes and would be replaced with proper certificates in production