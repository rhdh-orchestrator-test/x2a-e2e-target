# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are bash scripts for deploying Chef Automate and Chef Infra Server. The migration scope is relatively small, with most components already in Ansible format. The estimated timeline for complete migration is 1-2 weeks, with low complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS enabled using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache configuration, SSL certificate generation, virtual host setup

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables vulnerable SSL protocols, enables TLSv1.2

- **InSpec Tests**:
    - Description: Chef InSpec tests for verifying HTTPS functionality and SSH security compliance
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: Port verification, HTTPS content verification, SSL protocol verification, SSH configuration compliance

- **Chef Automate Deployment**:
    - Description: Bash script to deploy Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Infra Server installation, user and organization creation

- **Chef Server Deployment**:
    - Description: Bash script to deploy Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Infra Server installation, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests - will need to be replaced with Ansible-native testing framework like Molecule
- `index.html`: Simple HTML file used for testing - can be directly used in Ansible

### Target Details

Analyzing the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with Ansible Lint for static analysis
  - Option 3: Use Molecule for comprehensive testing
  - Option 4: Consider migrating to ansible-test framework

- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing

- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or open-source alternatives:
  - AWX (open-source upstream of Ansible Tower)
  - Ansible Automation Platform (commercial)

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL. Ensure proper SSL/TLS configuration is maintained during migration.
  - Migration approach: Preserve the same SSL configuration parameters in the Ansible playbooks
  
- **SSH Security**: InSpec tests verify SSH root login is disabled. Ensure this security check is maintained.
  - Migration approach: Convert InSpec tests to Ansible assert tasks or Molecule verify tests

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates are generated in the playbook - consider using ansible-vault for storing private keys

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing will require understanding the compliance requirements and implementing equivalent checks.
  - Mitigation: Use Ansible's assert module for basic checks, and consider Molecule for more complex verification

- **Chef Automate Deployment**: The Chef Automate deployment scripts need to be converted to Ansible playbooks.
  - Mitigation: Create Ansible roles for deploying alternative infrastructure management tools

### Migration Order

1. **website_https.yml** (already in Ansible format, low risk)
2. **poodle_fix.yml** (already in Ansible format, low risk)
3. **InSpec Tests** (moderate complexity, convert to Ansible testing framework)
4. **Chef Deployment Scripts** (high complexity, requires architectural decisions on replacement)

### Assumptions

1. The primary goal is to move away from Chef components while maintaining the same functionality
2. The InSpec tests are critical for compliance and their functionality must be preserved
3. A replacement for Chef Automate/Infra Server is required
4. The target environment will continue to be Ubuntu 20.04 or compatible
5. The self-signed certificate approach is acceptable for the migrated solution
6. The hardcoded credentials in the deployment scripts are for demonstration purposes only and will be properly secured in the migrated solution