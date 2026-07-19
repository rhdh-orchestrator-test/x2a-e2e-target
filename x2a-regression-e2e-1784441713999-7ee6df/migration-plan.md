# MIGRATION FROM CHEF AND ANSIBLE TO ANSIBLE

This repository contains a mix of Chef deployment scripts and Ansible playbooks that need to be consolidated into a unified Ansible approach. The migration is relatively straightforward as most configuration is already in Ansible format, with the primary focus on replacing Chef server deployment scripts and ensuring InSpec tests can be integrated into an Ansible workflow. Estimated timeline: 1-2 weeks.

## Module Migration Plan

This repository contains Chef and Ansible technologies that need individual migration planning:

### MODULE INVENTORY

- **chef-and-ansible**:
    - Description: Ansible playbooks for configuring HTTPS websites with Apache and InSpec tests for compliance verification
    - Path: chef-and-ansible
    - Technology: Ansible with Chef InSpec
    - Key Features: Apache HTTPS configuration, SSL/TLS security settings, InSpec compliance tests

- **setup-automate**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef deployment
    - Key Features: Chef Automate deployment, Chef Infra Server setup, user and organization creation

### Infrastructure Files

- `chef-and-ansible/website_https.yml`: Ansible playbook that configures an Apache web server with HTTPS support. Migration considerations: Already in Ansible format, can be used as-is with minor adjustments.
- `chef-and-ansible/poodle_fix.yml`: Ansible playbook that fixes SSL configuration in Apache to mitigate POODLE vulnerability. Migration considerations: Already in Ansible format, can be used as-is.
- `chef-and-ansible/kitchen.yml`: Test Kitchen configuration for testing Ansible playbooks with InSpec. Migration considerations: Replace with Ansible-native testing framework like Molecule.
- `chef-and-ansible/tests/website_https_verify.rb`: InSpec test for verifying HTTPS website configuration. Migration considerations: Convert to Ansible testing framework or maintain InSpec for testing.
- `chef-and-ansible/tests/ssh_profile.rb`: InSpec profile for SSH security compliance. Migration considerations: Convert to Ansible testing framework or maintain InSpec for testing.
- `setup-automate/deploy-automate.sh`: Bash script for deploying Chef Automate and Chef Infra Server. Migration considerations: Replace with Ansible playbook for deploying alternative configuration management or compliance tools.
- `setup-automate/deploy-chef-server.sh`: Bash script for deploying Chef Infra Server. Migration considerations: Replace with Ansible playbook for deploying alternative configuration management tools.

### Target Details

Analyze the source repository to determine target environment specifications:

- **Operating System**: Ubuntu 20.04 (identified from kitchen.yml and apt package manager usage in Ansible playbooks)
- **Virtual Machine Technology**: Vagrant (identified from kitchen.yml driver configuration)
- **Cloud Platform**: Not specified, appears to be platform-agnostic with potential for on-premises or cloud deployment (based on comments in setup scripts)

## Migration Approach

### Key Dependencies to Address

- **Chef Automate/Infra Server**: Replace with Ansible AWX/Tower for web UI and job scheduling
- **InSpec (latest)**: Options include:
  1. Continue using InSpec with Ansible for compliance testing
  2. Migrate to Ansible-native solutions like ansible-lint or Ansible Molecule
  3. Use alternative compliance tools like OpenSCAP with Ansible integration

### Security Considerations

- **SSL/TLS Configuration**: The existing playbooks configure Apache with TLS 1.2 and disable older protocols. Ensure this security practice is maintained in the migrated solution.
- **SSH Hardening**: The InSpec profile checks for SSH root login disablement. Ensure this security check is maintained in the Ansible-based solution.
- **Vault/secrets management**: For each module, identify credential patterns:
  - setup-automate: Hardcoded credentials in scripts (username, password) should be moved to Ansible Vault
  - chef-and-ansible: SSL certificate generation should use Ansible Vault for storing private keys
  - Count of credentials detected: 3 (username, password, SSL private key)

### Technical Challenges

- **InSpec Integration**: Determining whether to maintain InSpec for compliance testing or migrate to an Ansible-native solution. Mitigation: Evaluate the complexity of existing InSpec tests and the feasibility of converting them to Ansible-native tests.
- **Chef Server Replacement**: Identifying the appropriate Ansible-based replacement for Chef Server functionality. Mitigation: Evaluate Ansible AWX/Tower as a replacement for Chef Server's web UI and job scheduling capabilities.

### Migration Order

1. **Ansible Playbooks** (Low risk, already in Ansible format)
   - website_https.yml
   - poodle_fix.yml

2. **Testing Framework** (Moderate complexity)
   - Convert Kitchen configuration to Ansible Molecule or maintain InSpec integration
   - Update or convert InSpec tests as needed

3. **Chef Server Deployment Scripts** (High complexity)
   - Create Ansible playbooks to replace Chef Automate and Chef Infra Server deployment scripts
   - Implement Ansible Vault for credential management

### Assumptions

1. The primary purpose of this repository is to demonstrate how Chef InSpec can be used alongside Ansible for compliance automation, not for production deployment.
2. The Chef Automate and Chef Infra Server deployment scripts are used for setting up a test environment, not for production deployment.
3. The target environment is Ubuntu 20.04 running on Vagrant VMs.
4. The migration will maintain the existing functionality while consolidating on Ansible as the primary configuration management tool.
5. InSpec may be retained for compliance testing if it provides value beyond what Ansible-native testing can provide.
6. The hardcoded credentials in the setup scripts are for demonstration purposes only and will be replaced with Ansible Vault in the migrated solution.