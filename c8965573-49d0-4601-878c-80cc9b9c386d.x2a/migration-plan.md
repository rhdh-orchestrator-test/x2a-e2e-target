# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus appears to be showing how Chef InSpec can be used alongside Ansible for compliance testing. Additionally, there are shell scripts for deploying Chef Automate and Chef Infra Server.

The migration scope is relatively small, as most of the Ansible components are already in place. The main migration tasks will involve:
1. Converting Chef InSpec tests to Ansible-native testing solutions
2. Migrating Chef Automate/Infra Server deployment scripts to Ansible playbooks
3. Ensuring all compliance checks are properly implemented in the Ansible ecosystem

Estimated timeline: 1-2 weeks for a small team (1-2 engineers)

## Module Migration Plan

This repository contains Chef InSpec tests and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Integration of Chef InSpec with Ansible for compliance testing
    - Path: chef-and-ansible
    - Technology: Mixed (Chef InSpec tests with Ansible playbooks)
    - Key Features: HTTPS website deployment, SSL/TLS compliance testing, Test Kitchen integration

- **setup-automate**:
    - Description: Deployment scripts for Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts
    - Key Features: Automated deployment of Chef infrastructure components, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification. Migration consideration: Replace with Ansible-native testing framework like Molecule.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying a secure HTTPS website. Migration consideration: Can be kept as-is or enhanced with Ansible best practices.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities. Migration consideration: Can be kept as-is or enhanced with Ansible best practices.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Migration consideration: Convert to Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Migration consideration: Convert to Ansible playbook.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's assert module for basic compliance checks
  - Option 2: Integrate with Ansible Lint for static analysis
  - Option 3: Use Molecule for comprehensive testing
  - Option 4: Consider integrating with OpenSCAP or DISA STIG tools

- **Test Kitchen**: Replace with Molecule for Ansible role/playbook testing

- **Chef Automate/Infra Server**: Replace with:
  - Ansible Tower/AWX for orchestration
  - Ansible Collections for configuration management
  - GitLab CI/GitHub Actions for pipeline automation

### Security Considerations

- **SSL/TLS Configuration**: The repository includes specific SSL/TLS hardening (disabling SSLv3, enabling TLSv1.2). Ensure these security configurations are maintained in the Ansible migration.
  - Migration approach: Use Ansible's crypto modules and templates to enforce the same security standards.

- **SSH Hardening**: The repository includes InSpec tests for SSH security (disabling root login). Ensure these checks are implemented in Ansible.
  - Migration approach: Use Ansible's openssh_config module to enforce SSH security settings.

- **Self-signed Certificates**: The playbooks generate self-signed certificates. Consider enhancing with Let's Encrypt integration.
  - Migration approach: Use Ansible's acme_certificate module for Let's Encrypt integration.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password)
  - Migration approach: Move credentials to Ansible Vault

### Technical Challenges

- **InSpec to Ansible Testing**: Converting InSpec tests to Ansible-native testing solutions will require careful mapping of test assertions.
  - Mitigation strategy: Create a mapping document for InSpec resources to Ansible modules/assertions.

- **Compliance Reporting**: Chef InSpec provides rich compliance reporting that needs to be replicated in Ansible.
  - Mitigation strategy: Integrate with Ansible Tower/AWX for reporting or consider additional tools like OpenSCAP.

- **Chef Server Deployment**: The Chef Server deployment scripts need to be converted to Ansible playbooks.
  - Mitigation strategy: Create equivalent Ansible roles for each component of the Chef infrastructure.

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format)
   - website_https.yml
   - poodle_fix.yml

2. **InSpec Tests** (Moderate complexity)
   - website_https_verify.rb
   - ssh_profile.rb

3. **Chef Deployment Scripts** (High complexity)
   - deploy-automate.sh
   - deploy-chef-server.sh

4. **Test Kitchen Configuration** (Final integration)
   - kitchen.yml

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being a production deployment.
2. The hardcoded credentials in the setup scripts are for demonstration purposes only.
3. The self-signed certificates are acceptable for the demonstration environment but would need to be replaced with proper certificates in production.
4. The target environment is Ubuntu 20.04 running on Vagrant VMs.
5. The migration will maintain the same level of compliance checking but using Ansible-native tools.
6. The current Test Kitchen setup is used for development/testing only and can be replaced with Ansible Molecule.
7. There are no external dependencies or integrations beyond what is visible in the repository.