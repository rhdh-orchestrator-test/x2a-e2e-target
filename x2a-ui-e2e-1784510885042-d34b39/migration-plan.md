# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mixed environment of Chef and Ansible components that need to be migrated to a unified Ansible solution. The repository primarily consists of:

1. Chef Automate and Chef Infra Server deployment scripts
2. Ansible playbooks with Chef InSpec testing components
3. Example configurations for web server deployment and security hardening

The migration complexity is **LOW to MEDIUM** as most components are already in Ansible format, with the main effort focused on replacing Chef InSpec testing with Ansible-native solutions and migrating Chef server deployment scripts to Ansible playbooks. Estimated timeline: 2-3 weeks for a complete migration.

## Module Migration Plan

This repository contains Chef and Ansible components that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks with Chef InSpec testing for deploying and securing web servers
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: HTTPS web server deployment, SSL/TLS security hardening, compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: Ansible playbook that deploys an Apache web server with HTTPS enabled. Migration considerations include preserving the SSL certificate generation and virtual host configuration.
  
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook that addresses SSL POODLE vulnerability by enforcing TLSv1.2. Migration considerations include preserving the security hardening approach.
  
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration considerations include replacing with Ansible-native testing solutions like Molecule.
  
- `chef-and-ansible/tests/website_https_verify.rb`: Chef InSpec test for verifying HTTPS configuration. Migration considerations include converting to Ansible-native testing frameworks.
  
- `chef-and-ansible/tests/ssh_profile.rb`: Chef InSpec profile for SSH security compliance. Migration considerations include converting to Ansible-native security testing.
  
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Migration considerations include creating equivalent Ansible playbook for infrastructure deployment.
  
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Migration considerations include creating equivalent Ansible playbook for infrastructure deployment.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and Apache package version in website_https.yml)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver configuration)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with Ansible Lint for static code analysis
  - Option 3: Use Molecule for comprehensive testing
  - Option 4: Consider integrating with OpenSCAP for compliance testing

- **Test Kitchen**: Replace with Molecule for Ansible role and playbook testing

- **Chef Automate/Infra Server**: Replace with Ansible AWX/Tower or other Ansible management platform

### Security Considerations

- **SSL/TLS Configuration**: The migration must preserve the TLS hardening in poodle_fix.yml that enforces TLSv1.2
  - Migration approach: Use Ansible's template module with equivalent configuration

- **SSH Hardening**: The SSH security profile in ssh_profile.rb needs to be implemented as Ansible tasks
  - Migration approach: Convert InSpec controls to Ansible tasks that enforce the same security policies

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be migrated to Ansible Vault
  - SSL certificate generation should use Ansible's crypto modules with proper secret management
  - Count of credentials detected: 3 (username, password, SSL private key)

### Technical Challenges

- **Testing Framework Migration**: Converting Chef InSpec tests to Ansible-native testing will require careful mapping of test assertions
  - Mitigation: Create a mapping document for InSpec resources to Ansible modules/assertions

- **Infrastructure Deployment**: Replacing Chef server deployment scripts with equivalent Ansible functionality
  - Mitigation: Use Ansible's package management and service modules to achieve the same deployment outcomes

### Migration Order

1. **chef-and-ansible/website_https.yml and poodle_fix.yml** (low risk, already in Ansible format)
   - Only needs minor adjustments to follow Ansible best practices

2. **InSpec Tests** (moderate complexity)
   - Convert to Ansible-native testing solutions

3. **Chef Server Deployment Scripts** (high complexity)
   - Create Ansible playbooks to replace the bash scripts for infrastructure deployment

### Assumptions

1. The target environment will continue to use Ubuntu 20.04 or compatible Linux distributions
2. The web server configurations (Apache with SSL) will remain functionally equivalent
3. Security requirements for SSH and HTTPS will remain the same
4. The organization does not require Chef-specific features that might not have direct Ansible equivalents
5. The migration will completely replace Chef components rather than maintaining a hybrid approach
6. Test coverage should remain equivalent or improve during the migration
7. The current Vagrant-based testing approach is suitable for the organization's needs