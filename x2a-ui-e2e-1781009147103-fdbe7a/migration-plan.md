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
    - Description: Apache web server configuration with SSL/TLS setup, virtual hosts, and security hardening
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Self-signed certificate generation, virtual host configuration, SSL/TLS security settings

- **poodle-vulnerability-fix**:
    - Description: Security patch for POODLE vulnerability in SSL configurations
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enforces TLSv1.2

- **website-https-compliance**:
    - Description: InSpec tests for verifying HTTPS website configuration and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening checks, HTTPS response validation, SSL/TLS protocol verification

- **ssh-security-compliance**:
    - Description: InSpec profile for SSH security compliance checking
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards (SRG-OS-000112)

- **chef-automate-deployment**:
    - Description: Automated deployment script for Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash script
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Automated deployment script for Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash script
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file for website testing
- `README.md`: Documentation files explaining the purpose of the examples

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - Option 1: Use ansible-lint for basic compliance checks
  - Option 2: Integrate with Ansible Automation Platform's compliance capabilities
  - Option 3: Keep InSpec as a standalone tool and call it from Ansible playbooks

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - ansible-test for collection testing

- **Vagrant**: Can be retained for local testing or replaced with:
  - Docker containers for lightweight testing
  - Cloud-based testing environments

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening that disables vulnerable protocols (SSLv3) and enforces TLSv1.2
  - Approach: Use Ansible's `lineinfile` or `template` modules to manage SSL configuration files

- **SSH Security**: The SSH root login restrictions must be maintained
  - Approach: Use Ansible's `lineinfile` or dedicated SSH modules to enforce SSH security settings

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates should be managed securely
  - Count of credentials detected:
    - website-https-configuration: 0 hardcoded credentials
    - poodle-vulnerability-fix: 0 hardcoded credentials
    - chef-automate-deployment: 3 credentials (username, email, password)
    - chef-server-deployment: 3 credentials (username, email, password)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to equivalent Ansible verification
  - Mitigation: Use Ansible assert modules or consider keeping InSpec as a verification tool called from Ansible

- **Certificate Management**: Ensuring proper handling of SSL certificates
  - Mitigation: Use Ansible's crypto modules (openssl_*) which are already in use in the current playbooks

- **Idempotency**: Ensuring all converted scripts and playbooks are properly idempotent
  - Mitigation: Thorough testing with multiple runs to verify consistent behavior

### Migration Order

1. **website-https-configuration** (low risk, already in Ansible)
   - Only needs review and potential refactoring to follow best practices

2. **poodle-vulnerability-fix** (low risk, already in Ansible)
   - Only needs review and potential refactoring to follow best practices

3. **chef-automate-deployment** and **chef-server-deployment** (moderate complexity)
   - Convert bash scripts to Ansible playbooks
   - Implement proper secret management with Ansible Vault

4. **website-https-compliance** and **ssh-security-compliance** (high complexity)
   - Decide on compliance testing strategy (keep InSpec or migrate to Ansible-native)
   - Implement the chosen approach

### Assumptions

1. The primary goal is to standardize on Ansible rather than maintain a hybrid Chef/Ansible environment
2. InSpec tests may need to be preserved for their compliance capabilities
3. The deployment scripts are for demonstration purposes and not production environments
4. The hardcoded credentials in scripts are not used in production environments
5. The Test Kitchen setup is primarily for demonstration and testing
6. The target environment will continue to be Ubuntu 20.04 or compatible systems
7. The migration does not need to address scaling to large environments
8. The self-signed certificates are acceptable for the demonstration environment