# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Ansible playbooks for configuring HTTPS websites with Apache
2. Chef InSpec tests for verifying compliance
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is **LOW** with an estimated timeline of **1-2 weeks** to fully convert all components to pure Ansible solutions. The primary focus will be on replacing Chef InSpec tests with Ansible-native testing solutions while preserving the existing Ansible playbooks.

## Module Migration Plan

This repository contains Chef and Ansible components that need individual migration planning:

### MODULE INVENTORY

- **website-https-configuration**:
    - Description: Apache web server configuration with HTTPS, self-signed certificates, and basic website deployment
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: SSL certificate generation, Apache virtual host configuration, website deployment

- **poodle-vulnerability-fix**:
    - Description: Security fix for POODLE vulnerability in Apache SSL configuration
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enforces TLSv1.2 for Apache

- **compliance-testing**:
    - Description: InSpec tests for verifying HTTPS website functionality and SSH security compliance
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: HTTPS verification, SSL protocol testing, SSH root login security check

- **chef-infrastructure-deployment**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash scripts
    - Key Features: Chef server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests
- `index.html`: Sample HTML file for website deployment testing

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be infrastructure-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Ansible Molecule for infrastructure testing
  - Option 2: ansible-test for module testing
  - Option 3: Integration with other testing frameworks like Serverspec or pytest

- **Test Kitchen**: Replace with:
  - Ansible Molecule for a complete testing workflow
  - Or retain Test Kitchen with Ansible provisioner if preferred

- **Chef Automate/Infra Server**: Replace deployment scripts with:
  - Ansible roles for compliance scanning
  - AWX/Ansible Tower for enterprise automation platform

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security improvements in the poodle_fix.yml playbook
  - Ensure TLSv1.2 enforcement is preserved
  - Consider updating to also include TLSv1.3 support

- **SSH Security Hardening**: The InSpec profile for SSH security must be converted to equivalent Ansible checks
  - Create Ansible tasks to enforce the same SSH root login restrictions
  - Consider expanding SSH hardening based on current best practices

- **Vault/secrets management**:
  - Hardcoded credentials detected in setup scripts (username: jtonello, password: password)
  - Replace with Ansible Vault for secure credential storage
  - Consider implementing lookup plugins for dynamic secret retrieval

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing solutions
  - Challenge: Maintaining the same level of compliance verification
  - Mitigation: Use Ansible assert modules and custom modules where needed

- **Chef Server Deployment**: Replacing Chef server deployment with equivalent Ansible functionality
  - Challenge: Determining if Chef server is still needed or can be fully replaced
  - Mitigation: Evaluate if AWX/Tower can replace Chef Automate functionality

### Migration Order

1. **website-https-configuration** (low risk, already in Ansible)
   - Review and optimize existing Ansible playbook
   - Add documentation and improve variable usage

2. **poodle-vulnerability-fix** (low risk, already in Ansible)
   - Integrate into the main website playbook
   - Update to include latest security best practices

3. **compliance-testing** (moderate complexity)
   - Convert InSpec tests to Ansible assertions or Molecule tests
   - Ensure all compliance checks are preserved

4. **chef-infrastructure-deployment** (high complexity)
   - Determine if Chef infrastructure is still needed
   - If not, create Ansible playbooks for equivalent compliance functionality
   - If yes, create Ansible playbooks to deploy Chef infrastructure

### Assumptions

1. The primary purpose of this repository is demonstrating Chef InSpec with Ansible rather than production deployment
2. The Chef components (InSpec, Automate, Infra Server) are intended to be replaced with Ansible-native solutions
3. The security compliance requirements must be maintained during migration
4. The target environment will remain Ubuntu 20.04 or compatible Linux distributions
5. No external dependencies or integrations beyond what's visible in the repository
6. No custom Chef cookbooks or resources are in use that would require complex migration
7. The deployment scripts are examples and not production-ready (contain hardcoded credentials)