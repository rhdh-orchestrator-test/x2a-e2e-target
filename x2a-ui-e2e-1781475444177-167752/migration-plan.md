# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating Chef InSpec for compliance automation alongside Ansible. The migration scope is relatively small, consisting primarily of Ansible playbooks with Chef InSpec tests and Chef Automate/Chef Server deployment scripts. The estimated timeline for migration is 1-2 weeks, with low complexity as most components are already in Ansible format.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Apache web server configuration with SSL/TLS setup and a simple "Hello World" website
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Security fix for the POODLE vulnerability in Apache by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening

- **chef-automate-deployment**:
    - Description: Deployment script for Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash script
    - Key Features: Chef Automate installation, user and organization creation

- **chef-server-deployment**:
    - Description: Deployment script for Chef Infra Server without Automate
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash script
    - Key Features: Chef Server installation, user and organization creation

- **inspec-compliance-tests**:
    - Description: Chef InSpec tests for website HTTPS and SSH security compliance
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: HTTPS verification, SSL/TLS protocol validation, SSH root login security check

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests - should be migrated to Ansible Molecule for testing
- `index.html`: Simple HTML file used in the website deployment - can be reused as-is in Ansible

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 LTS (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native solutions:
  - Option 1: Use ansible-lint for static analysis
  - Option 2: Integrate with Ansible Molecule for testing
  - Option 3: Convert InSpec tests to Ansible assert tasks
  - Option 4: Keep InSpec as a compliance tool but invoke it from Ansible

- **Test Kitchen**: Replace with Ansible Molecule for testing infrastructure

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening that disables SSLv3 and enables only TLSv1.2
- **SSH Security**: The InSpec profile checks for SSH root login being disabled, which should be maintained in the Ansible configuration
- **Self-signed Certificates**: The current implementation uses self-signed certificates; consider implementing proper certificate management
- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password)
  - No encryption or vault usage detected in the current implementation
  - Recommend implementing Ansible Vault for credential storage in the migrated solution

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to equivalent Ansible verification methods may require additional logic
  - Mitigation: Use ansible.builtin.assert or consider keeping InSpec for compliance testing
  
- **Chef Automate/Server Deployment**: The bash scripts for Chef Automate and Chef Server deployment need to be converted to Ansible roles
  - Mitigation: Create dedicated Ansible roles for infrastructure components

### Migration Order

1. **website_https.yml** (low risk, already in Ansible format)
2. **poodle_fix.yml** (low risk, already in Ansible format)
3. **InSpec Tests** (moderate complexity, requires conversion strategy)
4. **Chef Deployment Scripts** (higher complexity, requires full conversion to Ansible roles)

### Assumptions

1. The repository is primarily used for demonstration purposes rather than production deployment
2. The InSpec tests are intended to validate the Ansible configurations
3. The hardcoded credentials in the setup scripts are for demonstration only and would be replaced with proper secret management
4. The target environment is Ubuntu 20.04 LTS as specified in kitchen.yml
5. The migration will maintain the same functionality but improve security practices
6. No external dependencies or integrations beyond what's visible in the repository