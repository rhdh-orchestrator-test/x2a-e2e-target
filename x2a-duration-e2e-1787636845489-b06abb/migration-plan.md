# MIGRATION FROM ANSIBLE AND CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Ansible playbooks and Chef InSpec tests, along with Chef Automate/Infra Server setup scripts. The migration scope is relatively small, focusing on converting existing Ansible playbooks to a standardized Ansible structure while preserving the compliance testing capabilities currently provided by Chef InSpec. The estimated timeline for this migration is 1-2 weeks, with low complexity for the Ansible components and moderate complexity for replacing the InSpec testing framework.

## Module Migration Plan

This repository contains Ansible playbooks and Chef InSpec tests that need individual migration planning:

### MODULE INVENTORY

- **website_https**:
    - Description: Ansible playbook that configures Apache web server with HTTPS support using self-signed certificates
    - Path: chef-and-ansible/website_https.yml
    - Technology: Ansible
    - Key Features: Apache2 installation, SSL certificate generation, virtual host configuration

- **poodle_fix**:
    - Description: Ansible playbook that remediates SSL POODLE vulnerability by disabling SSLv3 and enabling only TLSv1.2
    - Path: chef-and-ansible/poodle_fix.yml
    - Technology: Ansible
    - Key Features: Apache SSL configuration hardening, service restart handlers

- **chef-automate-deploy**:
    - Description: Bash script for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate/deploy-automate.sh
    - Technology: Bash/Chef
    - Key Features: Chef Automate installation, Chef Server configuration, user and organization setup

- **chef-server-deploy**:
    - Description: Bash script for deploying standalone Chef Infra Server
    - Path: setup-automate/deploy-chef-server.sh
    - Technology: Bash/Chef
    - Key Features: Chef Server installation, user and organization setup

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks and InSpec tests. Migration will require converting to Ansible Molecule for testing.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS configuration. Will need conversion to Ansible-compatible testing framework.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec compliance profile for SSH security settings. Will need conversion to Ansible-compatible testing framework.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment

## Migration Approach

### Key Dependencies to Address

- **Test Kitchen (kitchen.yml)**: Replace with Ansible Molecule for testing Ansible roles and playbooks
- **Chef InSpec**: Replace with one of the following options:
  - Ansible's built-in assert module for basic testing
  - Molecule's verifier functionality
  - Integration with ansible-lint for compliance checking
  - OpenSCAP with Ansible for compliance automation

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the security hardening in the poodle_fix.yml playbook that enforces TLSv1.2 and disables older protocols
- **Self-signed Certificates**: The website_https.yml playbook generates self-signed certificates; consider implementing a more robust certificate management solution in Ansible
- **SSH Hardening**: The ssh_profile.rb InSpec test checks for SSH root login restrictions; ensure this security check is preserved in the Ansible implementation
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - No encrypted secrets were found in the current implementation, but proper secret management should be implemented in the migrated solution

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec tests to equivalent Ansible testing mechanisms will require careful mapping of InSpec resources to Ansible modules
  - Mitigation: Create custom Ansible modules or use community.general collection modules to replicate InSpec functionality
  
- **Chef Automate/Server Deployment**: The bash scripts for Chef Automate and Chef Server deployment need to be converted to Ansible roles
  - Mitigation: Create dedicated Ansible roles for infrastructure components with idempotent tasks

- **Testing Framework**: Establishing a new testing framework to replace the InSpec/Kitchen combination
  - Mitigation: Implement Molecule for testing with appropriate verifiers

### Migration Order

1. **website_https playbook** (low risk, already in Ansible format)
   - Convert to proper Ansible role structure
   - Implement idempotency improvements
   
2. **poodle_fix playbook** (low risk, already in Ansible format)
   - Convert to proper Ansible role structure
   - Ensure it can be applied independently or as part of the website_https role

3. **Testing Framework** (moderate complexity)
   - Set up Molecule testing infrastructure
   - Convert InSpec tests to appropriate Ansible testing mechanisms

4. **Chef Automate/Server Deployment Scripts** (high complexity)
   - Create Ansible roles to replace the bash scripts
   - Implement proper secret management with Ansible Vault

### Assumptions

1. The current Ansible playbooks are functional but may not follow best practices for role structure and organization
2. The InSpec tests are essential for compliance validation and must be preserved in some form
3. The Chef Automate and Chef Server deployment scripts are used for setting up infrastructure and not for ongoing configuration management
4. No external dependencies or integrations beyond what's visible in the repository
5. The target environment will continue to be Ubuntu 20.04 or compatible systems
6. The migration does not need to preserve Test Kitchen functionality specifically, but must maintain equivalent testing capabilities
7. No complex data structures or external data sources are being used that would complicate the migration