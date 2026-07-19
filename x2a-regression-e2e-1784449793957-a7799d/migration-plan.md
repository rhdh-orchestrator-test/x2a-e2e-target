# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of:

1. Two Ansible playbooks for configuring HTTPS websites and SSL security
2. Chef InSpec test profiles for compliance verification
3. Chef Automate and Chef Infra Server deployment scripts

The migration complexity is **LOW** with an estimated timeline of 1-2 weeks. The primary focus will be on standardizing the existing Ansible playbooks to follow best practices and converting the Chef InSpec tests to Ansible-native testing frameworks.

## Module Migration Plan

This repository contains Chef and Ansible components that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks with Chef InSpec tests for secure website deployment
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: HTTPS website deployment, SSL configuration, compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user/organization creation

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: Ansible playbook that deploys an Apache web server with HTTPS enabled. Migration considerations include preserving the SSL certificate generation and virtual host configuration.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook that addresses SSL POODLE vulnerability by enforcing TLSv1.2. Migration considerations include ensuring security hardening is maintained.
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration considerations include replacing with Ansible-native testing frameworks.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality. Migration considerations include converting to Ansible Molecule tests.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec compliance profile for SSH security. Migration considerations include converting to Ansible security role or Ansible Molecule tests.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Migration considerations include replacing with Ansible roles for configuration management server deployment.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Migration considerations include replacing with Ansible roles for configuration management server deployment.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and apt package manager usage in playbooks)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver configuration)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Ansible Molecule for infrastructure testing
  - Option 2: OVAL/OpenSCAP with ansible-compliance role
  - Option 3: Continue using InSpec but integrate with Ansible workflows

- **Test Kitchen**: Replace with:
  - Ansible Molecule for testing Ansible roles and playbooks
  - Ansible Playbook testing with Vagrant directly

- **Chef Automate/Infra Server**: Replace with:
  - AWX/Ansible Tower for enterprise automation platform
  - Ansible Semaphore for lightweight open-source alternative
  - GitLab CI/CD for pipeline-based automation

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL/TLS. Ensure the migration maintains:
  - Self-signed certificate generation
  - Proper TLS protocol configuration (TLSv1.2 enforcement)
  - Secure virtual host configuration

- **SSH Hardening**: The InSpec profile checks for SSH root login disablement. Ensure:
  - SSH hardening is implemented in Ansible roles
  - Compliance checks are maintained in the new testing framework

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - SSL certificates and keys should be managed securely
  - Count of credentials detected: 3 (username, password, and SSL key)

### Technical Challenges

- **Testing Framework Migration**: Converting InSpec tests to Ansible-native testing frameworks:
  - Challenge: InSpec has a domain-specific language for compliance testing
  - Mitigation: Use Ansible Molecule with testinfra or YAML-based assertions, or maintain InSpec as a separate tool called from Ansible

- **Configuration Management Platform**: Replacing Chef Automate/Infra Server:
  - Challenge: Chef Automate provides integrated compliance reporting
  - Mitigation: Implement AWX/Ansible Tower with compliance reporting plugins or integrate with external compliance tools

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format)
   - Refactor existing playbooks to follow Ansible best practices
   - Convert to roles for better reusability
   - Implement Ansible Vault for secrets management

2. **Testing Framework** (Moderate complexity)
   - Set up Ansible Molecule testing framework
   - Convert InSpec tests to Molecule/testinfra tests
   - Ensure compliance checks are maintained

3. **Deployment Scripts** (High complexity)
   - Create Ansible roles for deploying automation platforms
   - Replace Chef Automate/Infra Server with Ansible-based alternatives
   - Implement user/organization management through Ansible

### Assumptions

1. The primary purpose of this repository is demonstrating Chef InSpec with Ansible rather than production deployment
2. The existing Ansible playbooks are functional but may not follow best practices
3. The target environment is Ubuntu 20.04 running on Vagrant VMs
4. The security compliance requirements (SSH hardening, SSL configuration) must be maintained
5. The deployment scripts are examples and not used in production environments
6. No external dependencies or integrations beyond what's visible in the repository
7. No complex data migrations are required as this appears to be a demonstration repository
8. The migration will standardize on pure Ansible without Chef components