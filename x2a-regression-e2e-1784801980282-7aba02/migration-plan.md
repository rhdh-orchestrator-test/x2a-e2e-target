# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests, along with Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, focusing on converting existing Ansible playbooks to a standardized Ansible structure while preserving the compliance testing capabilities currently provided by Chef InSpec. The estimated timeline for migration is 1-2 weeks, with low to moderate complexity.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **website_https_verify**:
    - Description: Chef InSpec test profile that verifies HTTPS configuration on the web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test profile that verifies SSH security configuration (root login disabled)
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH configuration validation, compliance with security standards

- **automate-deploy**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deploy**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification
- `chef-and-ansible/index.html`: Sample HTML content for the web server
- `README.md`: Repository overview and purpose

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (used in kitchen.yml for testing)
- **Cloud Platform**: Not specified, appears to be platform-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible testing framework:
  - Option 1: Convert InSpec tests to Ansible assert modules
  - Option 2: Use Molecule with testinfra for testing
  - Option 3: Maintain InSpec as a separate testing tool but integrate with Ansible workflow

- **Test Kitchen**: Replace with:
  - Option 1: Molecule for Ansible role testing
  - Option 2: Ansible-specific CI/CD pipeline

- **Chef Automate/Infra Server**: Replace with:
  - Option 1: Ansible Tower/AWX for orchestration and management
  - Option 2: GitLab CI/CD or Jenkins for pipeline management

### Security Considerations

- **SSL Configuration**: The migration must preserve the security hardening in poodle_fix.yml
  - Ensure TLSv1.2 remains enabled and SSLv3 remains disabled
  - Maintain the same level of Apache security configuration

- **SSH Hardening**: Maintain the security controls verified by ssh_profile.rb
  - Ensure root login remains disabled
  - Preserve compliance with security standards referenced in the InSpec profile (SRG-OS-000112, V-38607)

- **Vault/secrets management**:
  - Hardcoded credentials in deploy-automate.sh and deploy-chef-server.sh scripts need to be moved to Ansible Vault
  - Count: 2 credential sets (username/password) in deployment scripts

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing will require careful mapping of test assertions
  - Mitigation: Consider using Ansible's assert module or molecule with testinfra for similar functionality

- **Self-signed Certificate Generation**: The current playbook uses Ansible's openssl modules for certificate generation
  - Mitigation: Ensure the migrated solution uses the same or equivalent modules to maintain security posture

- **Compliance Validation**: The current solution uses InSpec for compliance validation against security standards
  - Mitigation: Ensure the migrated solution can still validate compliance with referenced security standards

### Migration Order

1. **website_https.yml** (Priority 1): Core web server configuration playbook, relatively straightforward to standardize
2. **poodle_fix.yml** (Priority 1): Security-critical playbook, should be migrated early to maintain security posture
3. **InSpec Tests** (Priority 2): Convert or integrate testing framework after core playbooks are migrated
4. **Deployment Scripts** (Priority 3): Convert bash scripts to Ansible roles for Chef Automate/Server deployment

### Assumptions

1. The current Ansible playbooks are functional but may not follow best practices or a standardized structure
2. The InSpec tests are used for validation and compliance reporting
3. The deployment scripts are used for setting up Chef infrastructure, which will be replaced by Ansible Tower/AWX
4. The target environment will remain Ubuntu 20.04 or compatible Linux distributions
5. The security requirements and compliance standards referenced in the InSpec profiles must be maintained
6. The repository is primarily used for demonstration and educational purposes rather than production deployment
7. No external dependencies or inventory files are present beyond what's visible in the repository