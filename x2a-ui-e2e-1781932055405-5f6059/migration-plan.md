# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Ansible playbooks for configuring HTTPS websites with Apache
2. Chef InSpec tests for verifying compliance
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing functionality while standardizing on Ansible for all infrastructure provisioning.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https-configuration**:
    - Description: Apache web server configuration with SSL/TLS setup, virtual hosts, and security hardening
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Self-signed certificate generation, virtual host configuration, SSL/TLS security settings

- **poodle-vulnerability-fix**:
    - Description: Security patch for POODLE vulnerability in SSL/TLS configurations
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enforces TLSv1.2 for Apache

- **compliance-testing**:
    - Description: InSpec tests for verifying HTTPS configuration and SSH security settings
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: Port verification, HTTPS content validation, SSL/TLS protocol checks, SSH root login security checks

- **chef-server-deployment**:
    - Description: Automated deployment of Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization creation

- **chef-automate-deployment**:
    - Description: Automated deployment of Chef Automate with Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server integration, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `index.html`: Sample HTML content for website testing
- `README.md`: Documentation explaining the purpose of the examples

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - Option 1: Use ansible-lint for basic compliance checks
  - Option 2: Integrate with Ansible Automation Platform's compliance capabilities
  - Option 3: Maintain InSpec as a separate tool but invoke it from Ansible

- **Test Kitchen**: Replace with:
  - Option 1: molecule for Ansible role testing
  - Option 2: ansible-test for collection testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Automation Platform for centralized automation
  - AWX (open source version of Ansible Tower) for smaller deployments

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening that disables SSLv3 and enforces TLSv1.2
  - Approach: Create an Ansible role for Apache security hardening that includes these configurations

- **SSH Security**: The InSpec tests verify SSH root login is disabled
  - Approach: Create an Ansible role for SSH hardening that enforces this security practice

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates should be managed securely
  - Count of credentials detected:
    - chef-automate-deployment: 1 password
    - chef-server-deployment: 1 password

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to equivalent Ansible verification methods
  - Mitigation: Use assert modules in Ansible to perform similar validation checks, or maintain InSpec as a verification tool called from Ansible

- **Certificate Management**: Ensuring proper handling of SSL certificates
  - Mitigation: Use Ansible's crypto modules (openssl_*) consistently for certificate management

- **Idempotency**: Ensuring all converted scripts are properly idempotent
  - Mitigation: Careful use of Ansible state parameters and when conditions

### Migration Order

1. **website-https-configuration** (low risk, already in Ansible)
   - Review and optimize existing Ansible playbook
   - Convert to proper Ansible role structure

2. **poodle-vulnerability-fix** (low risk, already in Ansible)
   - Integrate into the Apache security role
   - Ensure idempotency of configuration changes

3. **compliance-testing** (moderate complexity)
   - Convert InSpec tests to Ansible assertions or maintain as separate InSpec tests
   - Ensure integration with CI/CD pipeline

4. **chef-server-deployment** and **chef-automate-deployment** (high complexity)
   - Replace with Ansible Automation Platform deployment
   - Migrate user and organization management to Ansible Tower/AWX

### Assumptions

1. The primary goal is to standardize on Ansible while maintaining the same functionality
2. The InSpec tests are valuable and should be preserved in some form
3. The deployment scripts for Chef Server and Automate will be replaced with equivalent Ansible Automation Platform deployment
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. The security requirements (TLS 1.2, SSH hardening) must be maintained
6. No external data sources or integrations beyond what's visible in the repository are required
7. The migration will include proper documentation and testing to ensure equivalent functionality