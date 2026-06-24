# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Two Ansible playbooks for configuring HTTPS websites and fixing SSL vulnerabilities
2. Chef InSpec test profiles for verifying compliance
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing functionality while standardizing on Ansible for all configuration management.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https-configuration**:
    - Description: Apache web server configuration with HTTPS setup, self-signed certificates, and virtual host configuration
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: SSL certificate generation, Apache virtual host configuration, website deployment

- **poodle-vulnerability-fix**:
    - Description: Security fix for POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **https-compliance-tests**:
    - Description: InSpec tests to verify HTTPS configuration and website availability
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening verification, HTTPS response validation, SSL protocol verification

- **ssh-security-compliance**:
    - Description: InSpec profile to verify SSH security configuration (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance checks with STIG references

- **chef-server-deployment**:
    - Description: Deployment script for Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash script
    - Key Features: Chef server installation, user and organization creation

- **chef-automate-deployment**:
    - Description: Deployment script for Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash script
    - Key Features: Chef Automate installation, Chef server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file for website testing

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - Option 1: Use ansible-lint for basic compliance checks
  - Option 2: Integrate with Ansible Automation Platform's compliance capabilities
  - Option 3: Keep InSpec as a standalone tool but invoke it from Ansible

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role/playbook testing
  - ansible-test for collection testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Automation Platform for centralized automation
  - AWX (open source upstream of Ansible Tower) if budget is a concern

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook
  - Ensure TLSv1.2 remains the minimum protocol version
  - Consider updating to also include TLSv1.3 support

- **SSH Hardening**: Maintain the SSH security controls verified by the InSpec profile
  - Create equivalent Ansible tasks to enforce SSH root login restrictions
  - Consider expanding SSH hardening based on current best practices

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates should be managed securely

### Technical Challenges

- **Compliance Testing**: The primary challenge is maintaining the compliance testing capabilities currently provided by InSpec
  - Solution: Evaluate ansible-lint, OpenSCAP integration, or continued use of InSpec called from Ansible

- **Test Kitchen to Molecule Migration**: Converting the test workflow
  - Solution: Create equivalent Molecule scenarios for the existing Test Kitchen configurations

- **Chef Server Deployment**: Replacing Chef server deployment scripts
  - Solution: Create Ansible playbooks to deploy alternative infrastructure (AAP/AWX)

### Migration Order

1. **website-https-configuration** (low risk, already in Ansible)
   - Review and optimize existing Ansible playbook
   - Convert to Ansible role structure for better reusability

2. **poodle-vulnerability-fix** (low risk, already in Ansible)
   - Review and optimize existing Ansible playbook
   - Consider merging with website-https-configuration as a security role

3. **compliance-tests** (moderate complexity)
   - Evaluate compliance testing options
   - Implement chosen solution (ansible-lint, OpenSCAP, or InSpec integration)

4. **chef-server-deployment** (high complexity)
   - Create Ansible playbooks for deploying alternative infrastructure

### Assumptions

1. The primary purpose of this repository is demonstrating Chef InSpec with Ansible rather than production deployment
2. The target environment will continue to be Ubuntu 20.04 or compatible
3. Vagrant will continue to be used for development/testing environments
4. The security compliance requirements (STIG references) must be maintained in the new solution
5. Self-signed certificates are acceptable for the demonstration environment
6. The hardcoded credentials in the deployment scripts are for demonstration purposes only