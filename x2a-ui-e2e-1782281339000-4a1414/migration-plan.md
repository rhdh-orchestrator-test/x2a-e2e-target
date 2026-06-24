# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec testing profiles and Ansible playbooks that are used together to deploy and validate secure web server configurations. The primary focus appears to be demonstrating how Chef InSpec can be used alongside Ansible for compliance automation, as referenced in a Progress Chef white paper. The repository also includes Chef Automate and Chef Infra Server deployment scripts.

The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate. The complexity is low to moderate, as we need to convert InSpec tests to Ansible-compatible testing frameworks. Estimated timeline: 1-2 weeks for a complete migration, including testing and documentation.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that deploys an Apache web server with HTTPS configuration using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test profile that validates HTTPS configuration and website availability
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test profile that validates SSH security configuration (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, security compliance checks with STIG references

- **chef-automate-deployment**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Bash script for deploying Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec tests
- `index.html`: Sample HTML file used in the web server deployment

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's built-in `assert` module for basic validation
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use pytest-ansible for Python-based testing
  - Option 4: Convert InSpec tests to Ansible roles with test tasks

- **Test Kitchen**: Replace with Molecule for Ansible role testing
  - Molecule provides similar functionality for testing Ansible roles with various drivers and verifiers

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening present in the poodle_fix.yml playbook
  - Ensure the SSLProtocol settings are preserved to disable vulnerable protocols
  - Consider updating to include newer TLS versions (TLS 1.3) if appropriate

- **SSH Hardening**: The SSH security checks in ssh_profile.rb need to be maintained
  - Convert the InSpec controls to Ansible assertions or include them in an Ansible security role
  - Preserve the security metadata (STIG IDs, CCI references) in comments or documentation

- **Vault/secrets management**:
  - Hardcoded credentials detected in setup scripts (username, password)
  - Recommendation: Replace with Ansible Vault for secure credential storage

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-compatible testing frameworks
  - Challenge: InSpec provides domain-specific language for compliance testing that doesn't directly map to Ansible
  - Mitigation: Use a combination of Ansible assert modules and custom modules where needed, or maintain InSpec as a separate testing tool called from Ansible

- **Chef Automate/Server Deployment**: Replacing Chef infrastructure deployment scripts
  - Challenge: The deployment scripts set up Chef-specific infrastructure that may not have direct Ansible equivalents
  - Mitigation: If Chef infrastructure is still needed, keep these scripts separate; otherwise, replace with Ansible roles for deploying alternative compliance and configuration management tools

### Migration Order

1. **website_https.yml** (low risk, already in Ansible)
   - Review and optimize the existing Ansible playbook
   - Convert to a proper Ansible role structure with variables, handlers, and tasks separation

2. **poodle_fix.yml** (low risk, already in Ansible)
   - Review and optimize the existing Ansible playbook
   - Integrate with the website_https role as an optional security enhancement

3. **InSpec Tests** (moderate complexity)
   - Convert website_https_verify.rb to Ansible assertions or Molecule tests
   - Convert ssh_profile.rb to Ansible security role checks

4. **Chef Deployment Scripts** (high complexity, dependencies)
   - Determine if Chef infrastructure is still needed
   - If not, replace with Ansible roles for alternative compliance tooling

### Assumptions

1. The primary goal is to migrate all functionality to pure Ansible without relying on Chef components
2. The InSpec tests are used primarily for validation and could be replaced with Ansible-native testing
3. The deployment scripts for Chef Automate and Chef Server may not be needed if moving away from Chef entirely
4. The target environment will continue to be Ubuntu 20.04 or compatible systems
5. Vagrant will continue to be used for development/testing environments
6. The security requirements (STIG compliance, SSL hardening) must be maintained in the Ansible implementation
7. No external data sources or integrations are present beyond what's visible in the repository
8. The migration will maintain the same level of idempotence and error handling as the original implementation