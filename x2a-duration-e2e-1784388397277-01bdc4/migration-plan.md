# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations that need to be migrated to a unified Ansible solution. The repository primarily consists of:

1. Chef Automate and Chef Infra Server deployment scripts in the `setup-automate` directory
2. Ansible playbooks for configuring HTTPS websites with Apache in the `chef-and-ansible` directory
3. Chef InSpec tests for compliance verification in the `chef-and-ansible/tests` directory

The migration complexity is relatively low as most of the repository already contains Ansible playbooks. The main focus will be on replacing the Chef Automate and Chef Infra Server deployment scripts with equivalent Ansible roles and playbooks. The estimated timeline for this migration is 1-2 weeks, depending on the complexity of the Chef Automate replacement.

## Module Migration Plan

This repository contains Chef deployment scripts and Ansible playbooks that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for configuring HTTPS websites with Apache and InSpec tests for compliance verification
    - Path: chef-and-ansible (VERIFIED - directory exists)
    - Technology: Ansible and Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL/TLS security settings, InSpec compliance tests
    - Contents: README.md, index.html, kitchen.yml, poodle_fix.yml, tests directory, website_https.yml

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate (VERIFIED - directory exists)
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server deployment, user and organization creation
    - Contents: deploy-automate.sh, deploy-chef-server.sh

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: Ansible playbook for configuring Apache with HTTPS. Migration considerations include preserving the SSL certificate generation and virtual host configuration.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities in Apache. Migration considerations include ensuring the security hardening is maintained.
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec. Migration considerations include replacing with Ansible Molecule or maintaining Test Kitchen for testing.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website configuration. Migration considerations include converting to Ansible test framework or maintaining InSpec for testing.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance. Migration considerations include converting to Ansible test framework or maintaining InSpec for testing.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate. Migration considerations include replacing with Ansible playbook for alternative configuration management solution.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Migration considerations include replacing with Ansible playbook for alternative configuration management solution.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and apt package manager usage in Ansible playbooks)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver configuration)
- **Cloud Platform**: Not specified, but the scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef Automate and Chef Infra Server**: Replace with Ansible AWX/Tower or another configuration management solution
- **InSpec (latest)**: Either maintain InSpec for compliance testing or migrate to Ansible-native testing frameworks
- **Apache2 (2.4.41-4ubuntu3.10)**: Maintain the same version in Ansible playbooks for consistency
- **OpenSSL**: Maintain for SSL certificate generation
- **Test Kitchen with Vagrant**: Consider replacing with Ansible Molecule for testing or maintain Test Kitchen

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening for Apache that disables SSLv3 and only enables TLSv1.2
- **SSH Security**: The InSpec profile for SSH security must be maintained or converted to equivalent Ansible checks
- **Self-signed Certificates**: The process for generating self-signed certificates should be preserved
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificate and key files need secure handling
  - Count of credentials detected: 3 (username, password, and SSL key)

### Technical Challenges

- **Chef Automate Replacement**: Determining the appropriate replacement for Chef Automate functionality in an Ansible-only environment. Mitigation strategy: Evaluate Ansible AWX/Tower as a replacement or consider maintaining Chef Automate as a separate system.
- **InSpec Testing**: Deciding whether to maintain InSpec for compliance testing or migrate to Ansible-native testing. Mitigation strategy: Evaluate the complexity of converting InSpec tests to Ansible and decide based on team expertise and long-term maintenance considerations.
- **Configuration Management Workflow**: Establishing a workflow that replaces the Chef Server-based configuration management approach. Mitigation strategy: Design an Ansible-based workflow that provides similar functionality for managing configurations across multiple systems.

### Migration Order

1. **Ansible Playbooks** (chef-and-ansible/website_https.yml, chef-and-ansible/poodle_fix.yml): Low risk as they are already in Ansible format, may need minor adjustments for consistency
2. **Testing Framework** (chef-and-ansible/tests): Moderate complexity, decide whether to maintain InSpec or convert to Ansible-native testing
3. **Chef Deployment Scripts** (setup-automate): High complexity, requires designing a replacement for Chef Automate and Chef Infra Server functionality

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation, as indicated in the chef-and-ansible/README.md
2. The Chef deployment scripts are used for setting up a Chef environment that would be used in conjunction with Ansible and InSpec
3. The target environment is Ubuntu 20.04 running on Vagrant VMs
4. The security requirements include TLS 1.2 support and disabled SSLv3
5. The repository is primarily for demonstration purposes rather than production use, given the hardcoded credentials and simplified configurations
6. The migration should maintain the compliance testing capabilities currently provided by InSpec
7. The Apache configuration is a simple example and not a complex production configuration
8. There are no external dependencies beyond what is explicitly installed in the playbooks and scripts