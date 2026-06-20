# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible components focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Ansible playbooks for configuring HTTPS websites with Apache
2. Chef InSpec tests for verifying compliance
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is **LOW** with an estimated timeline of 1-2 weeks. The primary focus will be on preserving the InSpec testing capabilities while standardizing on Ansible for all infrastructure provisioning.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https-configuration**:
    - Description: Apache web server configuration with HTTPS/SSL setup, self-signed certificates, and virtual host configuration
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: SSL certificate generation, Apache virtual host configuration, website deployment

- **poodle-vulnerability-fix**:
    - Description: Security fix for POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2 in Apache
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **compliance-testing**:
    - Description: Chef InSpec tests for verifying HTTPS configuration and SSH security compliance
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: HTTPS verification, SSL protocol testing, SSH root login security check

- **chef-infrastructure-deployment**:
    - Description: Shell scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash
    - Key Features: Chef server deployment, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests - will need to be updated to use Ansible-native testing framework or adapted to work with pure Ansible
- `index.html`: Sample HTML file used in the website deployment - can be directly reused in Ansible

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic compliance checks
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Keep InSpec as a standalone tool and call it from Ansible

- **Test Kitchen**: Replace with:
  - Option 1: Ansible Molecule for testing
  - Option 2: Adapt existing kitchen.yml to work with pure Ansible

- **Chef Automate/Infra Server**: Replace with:
  - Option 1: Ansible AWX/Tower for centralized management
  - Option 2: GitOps approach with CI/CD pipeline

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in the POODLE fix playbook
  - Ensure TLSv1.2 remains enforced and SSLv3 remains disabled
  - Consider updating to include TLSv1.3 support

- **SSH Security**: Maintain the SSH root login restrictions verified by the InSpec tests
  - Implement as Ansible tasks that configure sshd_config

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - SSL certificates should be managed securely, potentially using ansible-vault for private keys

### Technical Challenges

- **InSpec Testing**: Determining the best approach to replace or integrate Chef InSpec tests
  - Mitigation: Evaluate Ansible's native assertion capabilities and consider keeping InSpec as a complementary tool if needed

- **Test Kitchen Integration**: Replacing the Test Kitchen workflow
  - Mitigation: Implement Molecule testing framework which is designed for Ansible

- **Chef Server Deployment**: Replacing Chef server deployment scripts
  - Mitigation: Create equivalent Ansible playbooks for AWX/Tower deployment or implement a GitOps approach

### Migration Order

1. **website-https-configuration** (low risk, already in Ansible)
   - Review and optimize existing Ansible playbook
   - Add idempotency improvements if needed

2. **poodle-vulnerability-fix** (low risk, already in Ansible)
   - Review and optimize existing Ansible playbook
   - Consider merging with the website-https-configuration playbook

3. **compliance-testing** (moderate complexity)
   - Convert InSpec tests to Ansible assertions or Molecule tests
   - Ensure all compliance checks are preserved

4. **chef-infrastructure-deployment** (high complexity)
   - Create Ansible playbooks to replace Chef server deployment scripts
   - Implement secure credential management with Ansible Vault

### Assumptions

1. The primary purpose of this repository is demonstration/educational rather than production use
2. The InSpec tests are a critical component that must be preserved in functionality
3. There are no external dependencies or integrations beyond what's visible in the repository
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. Vagrant will continue to be used for local development/testing
6. No custom Chef resources or complex Chef-specific functionality is in use
7. The migration will standardize on Ansible while maintaining the same level of security compliance testing