# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec tests for verifying compliance
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing functionality while standardizing on Ansible for all infrastructure provisioning.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https-configuration**:
    - Description: Apache web server configuration with SSL/TLS setup and self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle-vulnerability-fix**:
    - Description: Security fix for POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **compliance-testing**:
    - Description: InSpec tests for verifying HTTPS functionality and SSH security compliance
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: HTTPS verification, SSL protocol testing, SSH root login security check

- **chef-infrastructure-deployment**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash scripts
    - Key Features: Chef server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file for website testing

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - Option 1: Use ansible-lint for static analysis
  - Option 2: Use Molecule for testing Ansible roles
  - Option 3: Maintain InSpec as a compliance tool but integrate with Ansible workflows

- **Test Kitchen**: Replace with:
  - Option 1: Molecule for Ansible role testing
  - Option 2: Custom Ansible playbook for test environment provisioning

- **Chef Automate/Infra Server**: Replace with:
  - Option 1: Ansible AWX/Tower for centralized management
  - Option 2: GitOps workflow with CI/CD pipeline

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening that disables SSLv3 and enables only TLSv1.2
  - Approach: Create an Ansible role for Apache security hardening that includes the same SSL protocol restrictions

- **SSH Security Hardening**: Maintain the SSH root login restrictions
  - Approach: Create an Ansible role for SSH hardening that implements the same controls tested by the InSpec profile

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates should be managed securely, potentially using ansible-vault for private keys
  - Document the count and type of credentials detected per module:
    - chef-infrastructure-deployment: 1 user password in plain text

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to equivalent Ansible verification mechanisms
  - Mitigation: Consider using Ansible assert modules or maintaining InSpec as a separate compliance tool

- **Maintaining Compliance Focus**: The original repository demonstrates compliance automation with InSpec
  - Mitigation: Ensure the migration preserves the compliance testing capabilities, potentially by integrating InSpec with Ansible or by implementing equivalent checks in Ansible

### Migration Order

1. **website-https-configuration** (low risk, already in Ansible)
   - Review and optimize the existing Ansible playbook
   - Convert to a proper Ansible role structure

2. **poodle-vulnerability-fix** (low risk, already in Ansible)
   - Integrate into the Apache web server role
   - Ensure idempotency and proper testing

3. **compliance-testing** (moderate complexity)
   - Decide on testing strategy (maintain InSpec or convert to Ansible)
   - Implement equivalent tests in chosen framework

4. **chef-infrastructure-deployment** (high complexity)
   - Replace with Ansible roles for infrastructure management
   - Implement secure credential management

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec for compliance testing alongside Ansible, not for production deployment
2. The target environment is Ubuntu 20.04 running on Vagrant VMs
3. There are no external dependencies or integrations beyond what's visible in the repository
4. The security requirements (disabling SSLv3, restricting SSH root login) are critical to maintain
5. The deployment scripts for Chef Automate and Chef Infra Server are for demonstration purposes and may not need direct migration if the team is moving away from Chef
6. No specific performance requirements are documented for the web server configuration
7. The self-signed certificates are for testing only and would be replaced with proper certificates in production
8. There are no database or application components beyond the simple web server