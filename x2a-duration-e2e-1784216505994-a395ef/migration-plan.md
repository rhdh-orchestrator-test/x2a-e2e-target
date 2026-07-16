# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus is on using Chef InSpec for compliance testing alongside Ansible for configuration management. The migration scope is relatively small, with only a few Ansible playbooks and InSpec tests to migrate. The estimated timeline for migration is 1-2 weeks, with low complexity as most components are already in Ansible format.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Disables SSLv3 and enables only TLSv1.2 in Apache configuration

- **website_https_verify**:
    - Description: Chef InSpec test that verifies HTTPS functionality and security
    - Path: chef-and-ansible/tests/website_https_verify.rb
    - Technology: Chef InSpec
    - Key Features: Port listening check, HTTPS response validation, SSL protocol verification

- **ssh_profile**:
    - Description: Chef InSpec test that verifies SSH security configuration
    - Path: chef-and-ansible/tests/ssh_profile.rb
    - Technology: Chef InSpec
    - Key Features: SSH root login verification, compliance with security standards (SRG-OS-000112)

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh, setup-automate/deploy-chef-server.sh
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `index.html`: Sample HTML file used for testing web server functionality. Can be directly used in Ansible without modification.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be environment-agnostic

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with Ansible Lint for static analysis
  - Option 3: Use Molecule with testinfra for more comprehensive testing
  - Option 4: Keep InSpec as a standalone tool and call it from Ansible

- **Test Kitchen (latest)**: Replace with Molecule for Ansible role testing

### Security Considerations

- **SSL Configuration**: The migration must maintain the security hardening in the poodle_fix.yml playbook that disables SSLv3 and enables only TLSv1.2
- **SSH Security**: The SSH root login verification test must be preserved in the new testing framework
- **Self-signed Certificates**: The certificate generation process should be maintained or improved
- **Vault/secrets management**:
  - Hardcoded credentials in setup-automate scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets detected in deploy-automate.sh and deploy-chef-server.sh

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing frameworks may require different approaches for different test types:
  - Port checks can use Ansible's wait_for module
  - HTTP response checks can use uri module
  - SSL protocol verification may require custom modules or external commands
  
- **Chef Automate Deployment**: The Chef Automate and Chef Server deployment scripts need to be converted to Ansible playbooks, which will require:
  - Understanding the Chef Automate deployment process
  - Creating equivalent Ansible tasks for each step
  - Proper handling of user and organization creation

### Migration Order

1. **website_https.yml** (already in Ansible format, low risk)
2. **poodle_fix.yml** (already in Ansible format, low risk)
3. **InSpec Tests** (moderate complexity, requires framework selection)
4. **Chef Automate Deployment Scripts** (high complexity, requires deep understanding of Chef Automate)

### Assumptions

1. The primary goal is to consolidate all automation to Ansible, eliminating the dependency on Chef InSpec for testing
2. The target environment will continue to be Ubuntu 20.04 or compatible systems
3. Vagrant will continue to be used for development/testing environments
4. The security requirements (SSL/TLS configurations, SSH hardening) must be maintained
5. The Chef Automate and Chef Server deployment may be replaced with alternative solutions or kept as-is depending on requirements
6. No external data sources or databases are involved in the current setup
7. The migration will maintain the same level of idempotency and error handling as the current implementation
8. No complex orchestration or multi-server coordination is required