# MIGRATION FROM CHEF/ANSIBLE TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef and Ansible configurations focused on demonstrating how Chef InSpec can be used alongside Ansible for compliance automation. The migration scope is relatively small, consisting primarily of:

1. Ansible playbooks for configuring HTTPS websites
2. Chef InSpec tests for verifying compliance
3. Shell scripts for deploying Chef Automate and Chef Infra Server

The migration complexity is low to moderate, with an estimated timeline of 1-2 weeks. The primary focus will be on standardizing the existing Ansible playbooks and converting the Chef InSpec tests to Ansible-native testing frameworks.

## Module Migration Plan

This repository contains Chef and Ansible configurations that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks with Chef InSpec tests for HTTPS website deployment and compliance verification
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: HTTPS website configuration, SSL/TLS security settings, compliance testing

- **setup-automate**:
    - Description: Shell scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server configuration, user and organization setup

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: Ansible playbook that configures an Apache web server with HTTPS support. Migration considerations include preserving the SSL certificate generation and virtual host configuration.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook that addresses the POODLE vulnerability by updating SSL configurations. Migration considerations include ensuring security compliance is maintained.
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec. Migration considerations include replacing with Ansible-native testing frameworks.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website functionality. Migration considerations include converting to Ansible test framework.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec test for SSH security compliance. Migration considerations include converting to Ansible security tests.
- `setup-automate/deploy-automate.sh`: Shell script for deploying Chef Automate and Chef Infra Server. Migration considerations include determining if this functionality is needed in the Ansible environment.
- `setup-automate/deploy-chef-server.sh`: Shell script for deploying Chef Infra Server. Migration considerations include determining if this functionality is needed in the Ansible environment.

### Target Details

Based on the source repository analysis:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and apt package manager usage in playbooks)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver configuration)
- **Cloud Platform**: Not specified, but scripts are designed to work on both on-premises and cloud VMs (mentioned in script comments)

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec**: Replace with Ansible-native testing solutions:
  - Option 1: Use Ansible's `assert` module for basic compliance checks
  - Option 2: Integrate with Molecule for more comprehensive testing
  - Option 3: Use ansible-lint for static analysis of playbooks

- **Test Kitchen**: Replace with Molecule for Ansible playbook testing
  - Molecule provides similar functionality specifically designed for Ansible

### Security Considerations

- **SSL/TLS Configuration**: The migration must maintain the security hardening present in the current playbooks:
  - Disabling vulnerable protocols (SSL3)
  - Enforcing TLS 1.2
  - Proper certificate generation and management

- **SSH Security**: The SSH compliance tests check for root login restrictions, which must be preserved in the migrated solution.

- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates are generated dynamically but should be managed securely

### Technical Challenges

- **Testing Framework Migration**: Converting Chef InSpec tests to Ansible-native testing will require careful mapping of test assertions to ensure equivalent coverage.
  - Mitigation: Create a mapping document for InSpec resources to Ansible assertions

- **Chef Automate/Server Deployment**: Determining whether to include Chef server deployment in the Ansible migration or if this component is no longer needed.
  - Mitigation: Consult with stakeholders to determine if Chef components are still required or if they should be replaced with Ansible alternatives

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format)
   - Standardize and optimize existing playbooks
   - Implement Ansible best practices (roles, variables, etc.)

2. **Testing Framework** (Moderate complexity)
   - Convert InSpec tests to Ansible-native testing
   - Implement Molecule for playbook testing

3. **Chef Deployment Scripts** (High complexity, dependencies)
   - Determine if Chef components are still needed
   - If needed, convert shell scripts to Ansible roles for Chef deployment
   - If not needed, document the removal and any replacement functionality

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being a production deployment.
2. The Chef Automate and Chef Infra Server deployment scripts may not be needed in the final Ansible-only solution.
3. The security compliance requirements (HTTPS configuration, SSH hardening) must be maintained in the migrated solution.
4. The target environment will continue to be Ubuntu 20.04 running on Vagrant VMs.
5. There are no external dependencies or integrations beyond what is visible in the repository.
6. The migration will standardize on Ansible-native solutions rather than maintaining a hybrid Chef/Ansible approach.