# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of Ansible playbooks for configuring a web server with HTTPS and Chef InSpec tests for validation. Additionally, there are Chef Automate and Chef Infra Server deployment scripts. The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks to fully migrate all components to pure Ansible.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website-https**:
    - Description: Apache web server configuration with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle-fix**:
    - Description: Security fix for POODLE vulnerability in SSL by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **inspec-tests**:
    - Description: Chef InSpec tests for validating HTTPS configuration and SSH security
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: Port validation, HTTPS content verification, SSL protocol validation, SSH root login check

- **chef-deployment**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash scripts using Chef CLI tools
    - Key Features: Chef Automate deployment, Chef Infra Server configuration, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and validating with InSpec. Migration consideration: Replace with Ansible Molecule for testing.
- `index.html`: Sample HTML file for web server testing. Migration consideration: Can be used as-is or templated in Ansible.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - For compliance testing: Use ansible-lint for static analysis
  - For runtime validation: Use Ansible assert module or Molecule for testing
  - Alternative: Maintain InSpec as a separate tool called from Ansible

- **Test Kitchen**: Replace with Molecule for Ansible role testing

- **Chef Automate/Infra Server**: Evaluate replacement options:
  - Ansible Tower/AWX for orchestration and control
  - GitLab CI/CD or Jenkins for pipeline integration
  - Compliance management through OpenSCAP integration with Ansible

### Security Considerations

- **SSL/TLS Configuration**: The current implementation enforces TLSv1.2 and disables SSLv3. Migration should maintain or enhance this security posture.
  - Migration approach: Use Ansible's crypto modules to generate certificates and configure Apache with secure defaults

- **SSH Hardening**: InSpec tests validate SSH root login is disabled.
  - Migration approach: Include SSH hardening in Ansible roles using the openssh_config module

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - Self-signed certificates should be managed securely through Ansible Vault or external certificate management

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to equivalent Ansible validation mechanisms.
  - Mitigation: Use Ansible assert module for basic tests, consider maintaining InSpec for complex compliance testing, or evaluate alternative compliance tools compatible with Ansible.

- **Chef Automate Replacement**: Determining the appropriate replacement for Chef Automate functionality.
  - Mitigation: Evaluate Ansible Tower/AWX features against current Chef Automate usage to ensure all required functionality is covered.

### Migration Order

1. **website-https module** (low risk, already in Ansible): Review and optimize the existing Ansible playbook
2. **poodle-fix module** (low risk, already in Ansible): Integrate into the website-https playbook as a role
3. **inspec-tests** (moderate complexity): Convert to Ansible assertions or Molecule tests
4. **chef-deployment** (high complexity): Create Ansible playbooks for deploying Ansible Tower/AWX or alternative orchestration platform

### Assumptions

1. The primary purpose of this repository is demonstration/example code rather than production infrastructure
2. The InSpec tests are used for validation rather than continuous compliance monitoring
3. There are no external dependencies on Chef Automate beyond what's shown in the deployment scripts
4. The Apache web server configuration is relatively simple and doesn't have complex customizations
5. There are no external systems dependent on the Chef server API
6. The hardcoded credentials in the deployment scripts are for demonstration purposes only
7. There is no complex data bag or vault usage for secret management
8. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions