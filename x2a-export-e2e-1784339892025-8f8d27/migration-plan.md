# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef Automate/Infra Server deployment scripts and Ansible playbooks with Chef InSpec testing. The migration scope is relatively small, focusing on two main components:

1. Chef Automate and Chef Infra Server deployment scripts that need to be converted to Ansible playbooks
2. Existing Ansible playbooks with Chef InSpec testing that need to be consolidated into a pure Ansible solution

The migration complexity is **LOW to MEDIUM** with an estimated timeline of 1-2 weeks. The main challenge will be replacing Chef InSpec testing with equivalent Ansible testing solutions.

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for deploying a secure Apache web server with SSL/TLS configuration and InSpec testing
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL certificate generation, InSpec compliance testing

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation

### Infrastructure Files

- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for Ansible playbook testing with InSpec verification. Migration considerations include replacing with Ansible-native testing solutions like Molecule.
- `chef-and-ansible/website_https.yml`: Ansible playbook for deploying Apache with HTTPS. Can be directly incorporated into the Ansible solution with minimal changes.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities. Can be directly incorporated into the Ansible solution with minimal changes.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec tests for verifying HTTPS functionality. Needs to be converted to Ansible testing framework.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance. Needs to be converted to Ansible testing framework.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Needs to be converted to an Ansible playbook.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Needs to be converted to an Ansible playbook.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and apt package references)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic compliance checks
  - Option 2: Integrate with Ansible Lint for static code analysis
  - Option 3: Use Molecule for comprehensive testing
  - Option 4: Consider integrating with OpenSCAP for compliance testing

- **Test Kitchen**: Replace with Molecule for Ansible role testing
  - Molecule provides similar functionality for testing Ansible roles with various drivers (Vagrant, Docker, etc.)

- **Chef Automate/Infra Server**: Replace with Ansible AWX/Tower or other Ansible management solutions
  - AWX/Tower provides a web UI, API, and task engine for Ansible
  - Consider GitLab CI/CD or Jenkins for pipeline integration

### Security Considerations

- **SSL/TLS Configuration**: The current implementation configures Apache with TLS 1.2 and disables older protocols. This security practice should be maintained in the Ansible migration.
  - Migration approach: Use the same Ansible `replace` module approach as in the existing playbook.

- **SSH Security**: The repository includes InSpec tests for SSH security compliance.
  - Migration approach: Convert InSpec tests to Ansible assertions or integrate with OpenSCAP.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts: The Chef deployment scripts contain hardcoded usernames and passwords.
  - Migration approach: Use Ansible Vault to securely store credentials.
  - Count of credentials detected:
    - setup-automate: 3 credentials (username, password, organization name)

- **Certificate Management**: Self-signed certificates are generated in the Ansible playbook.
  - Migration approach: Maintain the same approach using Ansible's OpenSSL modules or consider integrating with a certificate management solution like Vault or Let's Encrypt.

### Technical Challenges

- **Testing Framework Migration**: Converting Chef InSpec tests to Ansible-native testing solutions.
  - Mitigation strategy: Map InSpec resources to equivalent Ansible modules and assertions. Consider using Ansible's `assert` module with appropriate conditions.

- **Chef Automate Functionality**: Ensuring all Chef Automate functionality is properly replaced.
  - Mitigation strategy: Clearly identify all Chef Automate features in use and map them to equivalent Ansible solutions. Consider AWX/Tower for web UI and API functionality.

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format)
   - Migrate `website_https.yml` and `poodle_fix.yml` with minimal changes
   - Update any deprecated Ansible syntax or modules

2. **Testing Framework** (Medium complexity)
   - Convert InSpec tests to Ansible-native testing solutions
   - Set up Molecule for testing infrastructure

3. **Chef Deployment Scripts** (Medium complexity)
   - Convert Chef Automate and Chef Infra Server deployment scripts to Ansible playbooks
   - Implement Ansible Vault for credential management

### Assumptions

1. The repository is primarily used for demonstration purposes, as indicated by the README.md mentioning "working examples" related to content created by Technical Product Marketing.
2. The Chef InSpec tests are used for compliance verification of the Ansible-deployed infrastructure.
3. The Chef Automate and Chef Infra Server deployment scripts are used for setting up a Chef environment, which will be replaced by an Ansible-based solution.
4. The target environment is Ubuntu 20.04 running on Vagrant VMs, but the solution should be adaptable to other environments.
5. There are no complex Chef cookbooks or recipes that need migration, only deployment scripts.
6. The hardcoded credentials in the deployment scripts are for demonstration purposes and will be replaced with secure credential management in the Ansible solution.