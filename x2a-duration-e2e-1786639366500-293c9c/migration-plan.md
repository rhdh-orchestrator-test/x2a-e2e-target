# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests, along with Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, focusing on converting existing Ansible playbooks to a more structured Ansible format while preserving the compliance testing capabilities currently provided by Chef InSpec. The estimated timeline for this migration is 1-2 weeks, with low to moderate complexity.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS configuration on the web server
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login check, compliance with security standards

- **deploy-automate**:
    - Description: Bash script that deploys Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server configuration, user and organization setup

- **deploy-chef-server**:
    - Description: Bash script that deploys Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization setup

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible Molecule for testing.
- `index.html`: Static HTML content for the web server. Can be directly used in Ansible templates.

## Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-compatible compliance testing tools:
  - Option 1: Convert InSpec tests to Ansible assert modules
  - Option 2: Integrate with ansible-lint for static analysis
  - Option 3: Maintain InSpec as a separate tool but invoke from Ansible

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

### Security Considerations

- **SSL Configuration**: The playbooks configure SSL for Apache. Migration should maintain or improve the security posture:
  - Ensure TLSv1.2 or higher is enforced
  - Consider adding modern cipher suite configurations
  - Implement proper certificate management

- **SSH Security**: The InSpec tests verify SSH security configurations:
  - Ensure root login remains disabled in migrated configurations
  - Maintain compliance with security standards referenced in the tests (SRG-OS-000112, V-38607, etc.)

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates should be managed securely

### Technical Challenges

- **InSpec Test Conversion**: Converting Chef InSpec tests to equivalent Ansible verification methods:
  - Solution: Use Ansible assert modules or consider maintaining InSpec as a separate tool invoked by Ansible

- **Compliance Reporting**: Maintaining compliance reporting capabilities:
  - Solution: Integrate with Ansible AWX/Tower for reporting or implement custom reporting solutions

- **Certificate Management**: Properly managing SSL certificates:
  - Solution: Use Ansible's crypto modules for certificate generation and management

### Migration Order

1. **website_https.yml** (Priority 1): Core web server configuration, relatively straightforward to migrate to Ansible roles
2. **poodle_fix.yml** (Priority 1): Security fix, should be integrated into the web server role
3. **InSpec Tests** (Priority 2): Convert to Ansible assertions or maintain as separate tests
4. **Chef Deployment Scripts** (Priority 3): Convert to Ansible roles for deploying monitoring/compliance tools

### Assumptions

1. The current setup uses Ansible playbooks with Chef InSpec for compliance testing, not Chef for configuration management
2. The target environment will continue to be Ubuntu 20.04 or compatible systems
3. Vagrant will continue to be used for development/testing environments
4. The self-signed certificates are acceptable for the environment (not production)
5. The hardcoded credentials in the deployment scripts are for testing purposes only
6. The compliance requirements (CCI-000774, etc.) will remain applicable in the migrated environment