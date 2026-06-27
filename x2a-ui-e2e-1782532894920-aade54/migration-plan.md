# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, with two main components: (1) Ansible playbooks with InSpec tests for a web server deployment and (2) Chef Automate/Chef Infra Server deployment scripts. The estimated timeline for migration is 1-2 weeks, with low complexity for the Ansible components (which need minimal changes) and medium complexity for the Chef server deployment scripts (which need to be converted to Ansible roles).

## Module Migration Plan

This repository contains Chef and Ansible configurations that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Apache web server deployment with HTTPS configuration, self-signed certificates, and a simple "Hello World" website
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: SSL/TLS configuration, Apache virtual host setup, self-signed certificate generation

- **poodle-fix**:
    - Description: Security fix for the POODLE vulnerability in Apache by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL module configuration, security hardening

- **chef-automate-deployment**:
    - Description: Chef Automate and Chef Infra Server deployment script with user and organization creation
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash script for Chef deployment
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization management

- **chef-server-deployment**:
    - Description: Chef Infra Server (standalone) deployment script with user and organization creation
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash script for Chef deployment
    - Key Features: Chef Server installation, user and organization management

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `tests/website_https_verify.rb`: InSpec test profile for verifying HTTPS website deployment
- `tests/ssh_profile.rb`: InSpec test profile for SSH security compliance
- `index.html`: Sample HTML file for website deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - Option 1: Continue using InSpec as a standalone tool called from Ansible
  - Option 2: Migrate tests to Ansible's assert module or ansible-lint
  - Option 3: Use Molecule for testing Ansible roles with testinfra

- **Test Kitchen**: Replace with:
  - Molecule for Ansible role testing
  - Ansible's built-in testing capabilities

- **Chef Automate/Chef Infra Server**: Replace with:
  - Ansible Automation Platform (AWX/Tower) for enterprise automation
  - Ansible Galaxy for role sharing
  - Git repositories for playbook/role management

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening that disables SSLv3 and enables only TLSv1.2
  - Approach: Create an Ansible role for Apache security hardening that includes the POODLE fix

- **SSH Hardening**: The InSpec profile checks for SSH root login disablement
  - Approach: Create an Ansible role for SSH hardening that implements the same controls

- **Vault/secrets management**:
  - Hardcoded credentials in Chef deployment scripts (username, password)
    - Replace with Ansible Vault for secure credential storage
  - Self-signed certificates in the Apache configuration
    - Use Ansible's crypto modules for certificate management

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to equivalent Ansible testing mechanisms
  - Mitigation: Consider keeping InSpec as a standalone tool or use Molecule with testinfra for similar functionality

- **Chef Server Deployment**: Replacing Chef server deployment with equivalent Ansible functionality
  - Mitigation: Create an Ansible role for deploying an Ansible control node with AWX/Tower

- **Compliance Automation**: Maintaining compliance automation capabilities without Chef InSpec
  - Mitigation: Implement compliance checks using Ansible's assert module or integrate with OpenSCAP

### Migration Order

1. **website-https module** (low risk, already in Ansible)
   - Refactor into a proper Ansible role structure
   - Update deprecated syntax if any
   - Improve variable handling

2. **poodle-fix module** (low risk, already in Ansible)
   - Integrate into the website-https role as a security task
   - Ensure idempotency

3. **InSpec Tests** (moderate complexity)
   - Either keep as-is and call from Ansible
   - Or convert to equivalent Ansible testing mechanisms

4. **Chef Deployment Scripts** (high complexity)
   - Create Ansible roles for deploying Ansible control infrastructure
   - Replace user/organization management with Ansible user management

### Assumptions

1. The primary goal is to move away from Chef while maintaining the same functionality
2. InSpec tests are valuable and should be preserved in some form
3. The deployment scripts are used for setting up automation infrastructure
4. The target environment will continue to be Ubuntu 20.04 or similar
5. Vagrant will continue to be used for development/testing environments
6. The security requirements (TLS 1.2, SSH hardening) must be maintained
7. No external dependencies or integrations beyond what's visible in the repository
8. The "Hello World" website is a simple example and not a production application