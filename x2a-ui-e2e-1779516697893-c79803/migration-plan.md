# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. There are also Chef Automate and Chef Infra Server deployment scripts. The migration scope is relatively small, as most of the infrastructure code is already in Ansible format, with Chef primarily used for testing and server deployment. The estimated timeline for complete migration is 1-2 weeks, with low complexity.

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
    - Key Features: Disables SSLv3, enables TLSv1.2 only

- **inspec_tests**:
    - Description: Chef InSpec tests for verifying HTTPS website functionality and SSH security compliance
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: Port listening checks, HTTP response validation, SSL protocol verification, SSH configuration validation

- **chef_deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash with Chef CLI
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration consideration: Replace with Ansible-native testing framework like Molecule.
- `index.html`: Simple HTML file used for testing. No migration needed.
- `README.md`: Documentation file. Update to reflect new Ansible-only approach.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but deployment scripts suggest on-premises or generic cloud VM usage

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with Ansible Lint for static analysis
  - Option 3: Use Molecule for comprehensive testing
  - Option 4: Consider migrating to ansible-compliance if advanced compliance testing is needed

- **Test Kitchen (latest)**: Replace with Molecule for Ansible role and playbook testing

- **Chef Automate/Infra Server**: Replace with Ansible Automation Platform or alternative infrastructure management:
  - Option 1: Ansible AWX/Tower for web UI and job scheduling
  - Option 2: GitLab CI/CD for pipeline-based automation
  - Option 3: Jenkins with Ansible plugins

### Security Considerations

- **SSL Configuration**: The current implementation properly disables SSLv3 and enables only TLSv1.2. Migration should maintain this security practice.
  - Migration approach: Ensure the same SSL hardening is applied in the migrated Ansible playbooks.

- **SSH Hardening**: InSpec tests verify SSH root login is disabled.
  - Migration approach: Implement equivalent checks using Ansible's assert module or Ansible Lint rules.

- **Self-signed Certificates**: The current implementation generates self-signed certificates.
  - Migration approach: Consider enhancing with Let's Encrypt integration for production environments.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Count: 2 credential sets in deployment scripts

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible assertions or other testing frameworks.
  - Mitigation: Create a mapping of InSpec resources to equivalent Ansible modules and assertions.

- **Chef Server Deployment**: Replacing Chef Server deployment with equivalent Ansible management infrastructure.
  - Mitigation: Document clear alternatives for each Chef Server function in the Ansible ecosystem.

### Migration Order

1. **website_https playbook** (already in Ansible, no migration needed)
2. **poodle_fix playbook** (already in Ansible, no migration needed)
3. **InSpec tests** (convert to Ansible-native testing)
4. **Chef deployment scripts** (convert to Ansible roles for deploying alternative infrastructure)

### Assumptions

1. The primary goal is to eliminate Chef dependencies while maintaining the same functionality.
2. The InSpec tests are critical for compliance validation and need equivalent functionality in the Ansible ecosystem.
3. The deployment scripts for Chef Automate and Chef Infra Server need to be replaced with equivalent infrastructure that can be managed by Ansible.
4. The target environment will continue to be Ubuntu 20.04 or compatible Linux distributions.
5. The self-signed certificate approach is acceptable, but might benefit from enhancement with trusted certificates.
6. The repository is primarily for demonstration purposes rather than production use, based on the educational nature of the README.
7. The hardcoded credentials in the deployment scripts are for demonstration purposes and would be replaced with secure credential management in production.