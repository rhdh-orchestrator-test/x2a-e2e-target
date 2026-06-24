# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Ansible playbooks for configuring HTTPS websites with security compliance
2. Chef InSpec tests for verifying compliance
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the compliance testing functionality while standardizing on Ansible for all infrastructure provisioning.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https-configuration**:
    - Description: Apache web server configuration with HTTPS, self-signed certificates, and security hardening
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: SSL/TLS configuration, virtual host setup, self-signed certificate generation

- **poodle-vulnerability-fix**:
    - Description: Security patch for POODLE vulnerability in SSL/TLS configuration
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enforces TLSv1.2

- **compliance-testing**:
    - Description: InSpec tests for verifying HTTPS configuration and SSH security compliance
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: Port verification, HTTPS content validation, SSL/TLS protocol security checks, SSH root login security checks

- **chef-infrastructure-deployment**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash scripts
    - Key Features: Chef server installation, user and organization creation, system configuration

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification
- `index.html`: Sample HTML content for the web server
- `deploy-automate.sh`: Script to deploy Chef Automate and Chef Infra Server
- `deploy-chef-server.sh`: Script to deploy Chef Infra Server only

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with on-premises focus

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic compliance checks
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Maintain InSpec as a separate tool but invoke it from Ansible

- **Test Kitchen**: Replace with:
  - Ansible Molecule for testing Ansible roles and playbooks
  - Molecule can use Vagrant as a driver similar to Test Kitchen

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Automation Platform for enterprise automation
  - AWX (open source version of Ansible Tower) for smaller deployments
  - GitLab CI/CD or GitHub Actions for pipeline-based automation

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening that disables vulnerable protocols (SSLv3) and enforces TLSv1.2
  - Approach: Create an Ansible role for Apache SSL hardening that implements the same security controls

- **SSH Security**: The InSpec profile checks for SSH root login restrictions
  - Approach: Create an Ansible role that enforces the same SSH security controls and includes verification tasks

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates should be managed securely, potentially using ansible-vault for private keys

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible verification tasks
  - Mitigation: Use Ansible's `uri` module for HTTP checks and `command`/`shell` modules with appropriate assertions for SSL verification

- **Maintaining Compliance Reporting**: InSpec provides structured compliance reporting
  - Mitigation: Consider implementing custom reporting using Ansible callback plugins or maintaining InSpec for testing only

- **Chef Server Deployment**: The Chef server deployment scripts need to be replaced
  - Mitigation: Create Ansible playbooks that deploy alternative infrastructure management solutions

### Migration Order

1. **website-https-configuration** (low risk, already in Ansible)
   - Review and optimize existing Ansible playbook
   - Convert to a proper Ansible role with variables

2. **poodle-vulnerability-fix** (low risk, already in Ansible)
   - Integrate into the HTTPS configuration role
   - Add additional security hardening based on current best practices

3. **compliance-testing** (moderate complexity)
   - Convert InSpec tests to Ansible verification tasks
   - Implement reporting mechanism

4. **chef-infrastructure-deployment** (high complexity)
   - Determine replacement infrastructure (Ansible AWX/Tower)
   - Create Ansible playbooks for deployment

### Assumptions

1. The primary purpose of this repository is demonstrating compliance automation, not production deployment
2. The InSpec tests are the most valuable components to preserve in functionality
3. There are no external dependencies on Chef beyond what's visible in the repository
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. Vagrant will continue to be used for development/testing environments
6. No custom Chef resources or complex Chef-specific functionality is in use
7. The hardcoded credentials in the deployment scripts are for demonstration only and will be replaced with secure practices