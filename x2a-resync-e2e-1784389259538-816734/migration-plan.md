# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations that need to be consolidated into a unified Ansible approach. The repository primarily consists of:

1. Ansible playbooks for configuring HTTPS websites with Apache
2. Chef InSpec tests for validating security compliance
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is **LOW to MEDIUM** as most of the content is already in Ansible format, with the main effort focused on converting InSpec tests to Ansible-compatible testing frameworks and replacing Chef Automate/Infra Server deployment scripts with Ansible equivalents.

**Estimated Timeline**: 2-3 weeks for a complete migration, including testing and validation.

## Module Migration Plan

This repository contains Chef and Ansible configurations that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for deploying and securing Apache web servers with HTTPS
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec tests
    - Key Features: SSL certificate generation, Apache configuration, virtual host setup, POODLE vulnerability fix

- **setup-automate**:
    - Description: Shell scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying Apache with HTTPS. Can be directly used in the migrated solution with minor optimizations.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL POODLE vulnerability. Can be integrated with the main Apache playbook.
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification. Migration should replace with Ansible-native testing framework like Molecule.
- `chef-and-ansible/index.html`: Sample HTML file for website testing. Can be directly used in Ansible content.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for validating HTTPS website. Should be converted to Ansible-compatible tests.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance. Should be converted to Ansible-compatible tests.
- `setup-automate/deploy-automate.sh`: Chef Automate deployment script. Should be replaced with Ansible playbook for infrastructure setup.
- `setup-automate/deploy-chef-server.sh`: Chef Server deployment script. Should be replaced with Ansible playbook for infrastructure setup.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and apt package references)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing frameworks:
  - Option 1: Use Ansible's built-in `assert` module for basic compliance checks
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis of playbooks

- **Test Kitchen**: Replace with Molecule for Ansible playbook testing and validation

- **Chef Automate/Infra Server**: Replace with:
  - AWX/Ansible Tower for orchestration and management
  - GitLab CI/CD or GitHub Actions for pipeline automation
  - Compliance automation using OpenSCAP or similar tools

### Security Considerations

- **SSL Configuration**: The current playbooks configure Apache with TLS 1.2 and disable older protocols. This security practice should be maintained in the migrated Ansible playbooks.

- **SSH Hardening**: The InSpec tests verify SSH root login is disabled. This check should be implemented in the migrated Ansible playbooks using the `ansible.posix.sshd_config` module.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates should be managed securely, potentially using ansible-vault for private keys
  - Count of credentials detected: 3 (username, password, and SSL private key)

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks will require careful mapping of test assertions to ensure equivalent coverage.
  - Mitigation: Create a mapping document for InSpec resources to Ansible modules/assertions

- **Chef Automate Replacement**: Replacing Chef Automate functionality with Ansible Tower/AWX will require planning for equivalent workflows.
  - Mitigation: Document Chef Automate usage patterns and map to equivalent Ansible Tower/AWX workflows

### Migration Order

1. **chef-and-ansible** (low risk, already in Ansible format)
   - Review and optimize existing Ansible playbooks
   - Convert InSpec tests to Ansible assertions or Molecule tests
   - Ensure equivalent coverage for security checks

2. **setup-automate** (high complexity)
   - Create Ansible playbooks to replace Chef Automate and Chef Server deployment
   - Implement secure credential management with Ansible Vault

### Assumptions

1. The current repository is used primarily for demonstration and educational purposes rather than production deployments (based on README references to white papers and examples).

2. The InSpec tests are intended to validate both Ansible-managed and potentially Chef-managed systems, suggesting a hybrid environment.

3. The Chef Automate and Chef Server deployment scripts are used for setting up infrastructure that may need to be replaced or maintained alongside new Ansible deployments.

4. The target environment is Ubuntu 20.04 running on Vagrant VMs, but the solution should be flexible enough to work on cloud platforms.

5. There are no complex Chef cookbooks or recipes that need migration beyond what's visible in the repository.

6. The security requirements include TLS 1.2 support and SSH hardening, which must be maintained in the migrated solution.