# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are bash scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the Ansible components are already in place. The main migration effort will involve:
1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Adapting the Chef Automate/Infra Server deployment scripts to Ansible playbooks

Estimated timeline: 1-2 weeks for a complete migration, with low complexity.

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that sets up an Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that addresses the POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **inspec_tests**:
    - Description: Chef InSpec tests for verifying HTTPS functionality and SSH security compliance
    - Path: chef-and-ansible/tests/
    - Technology: Chef InSpec
    - Key Features: Port listening checks, HTTPS content verification, SSL protocol verification, SSH configuration compliance

- **chef_deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/
    - Technology: Bash
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization creation

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and verifying with InSpec. Migration considerations include replacing with Ansible-native testing frameworks like Molecule.
- `index.html`: Simple HTML file used for testing. No migration needed as it's a static content file.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but the deployment scripts mention they can be used on "on-prem or cloud VM"

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with Ansible Lint for static analysis
  - Option 3: Use Molecule for comprehensive testing
  - Option 4: Consider integrating with OpenSCAP or DISA STIG tools

- **Test Kitchen**: Replace with Molecule for Ansible role testing

### Security Considerations

- **SSL Configuration**: The playbooks configure Apache with SSL/TLS. Ensure the migration maintains or enhances the security posture:
  - Maintain TLSv1.2 requirement and SSLv3 disablement
  - Consider upgrading to include TLSv1.3 support
  - Review certificate generation practices

- **SSH Hardening**: The InSpec tests verify SSH root login is disabled. Ensure this security check is maintained in the Ansible-native solution.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - Self-signed certificates are generated in the playbook; consider using Ansible Vault for storing pre-generated certificates or keys

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec's declarative testing syntax to Ansible's procedural approach may require careful mapping of test assertions.
  - Mitigation: Use Ansible's assert module with well-defined conditions that match the original InSpec tests.

- **Chef Server Deployment**: Converting the Chef Server deployment scripts to Ansible requires understanding of Chef's architecture.
  - Mitigation: Create an Ansible role specifically for Chef Server deployment, or consider if Chef Server is still needed after migration.

### Migration Order

1. **website_https playbook** (low risk, already Ansible): Review and optimize the existing Ansible playbook
2. **poodle_fix playbook** (low risk, already Ansible): Review and optimize the existing Ansible playbook
3. **InSpec tests** (moderate complexity): Convert to Ansible-native testing
4. **Chef deployment scripts** (high complexity): Convert to Ansible playbooks or evaluate if still needed

### Assumptions

1. The primary goal is to eliminate Chef dependencies while maintaining the same functionality.
2. The InSpec tests are essential for compliance verification and need to be preserved in some form.
3. The deployment of Chef Automate/Infra Server may no longer be necessary after migration to pure Ansible.
4. The target environment will continue to be Ubuntu 20.04 or compatible systems.
5. Vagrant will continue to be used for development/testing environments.
6. The security requirements (SSL/TLS configuration, SSH hardening) must be maintained or enhanced.
7. No external data sources or integrations are present beyond what's visible in the repository.