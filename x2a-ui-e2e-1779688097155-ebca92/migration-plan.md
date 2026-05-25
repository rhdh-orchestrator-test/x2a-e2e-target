# MIGRATION FROM CHEF TO ANSIBLE

## Executive Summary

This repository contains a mix of Chef InSpec tests and Ansible playbooks that are used together to demonstrate compliance automation. The primary focus is on migrating the Chef InSpec tests and Chef Automate/Chef Infra Server setup scripts to pure Ansible solutions. The migration scope is relatively small, with only a few InSpec test files and bash scripts for Chef server deployment. The estimated timeline for migration is 1-2 weeks, with low complexity as most of the infrastructure code is already in Ansible format.

## Module Migration Plan

This repository contains Chef InSpec tests and Chef server deployment scripts that need individual migration planning:

### MODULE INVENTORY

- **chef-inspec-tests**:
    - Description: Chef InSpec tests for validating HTTPS website configuration and SSH security settings
    - Path: chef-and-ansible/tests
    - Technology: Chef InSpec
    - Key Features: HTTPS validation, SSL/TLS protocol verification, SSH configuration compliance checks

- **chef-automate-deployment**:
    - Description: Bash scripts for deploying Chef Automate and Chef Infra Server
    - Path: setup-automate
    - Technology: Bash scripts for Chef server deployment
    - Key Features: User creation, organization setup, server configuration

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification. Migration consideration: Replace with Ansible Molecule for testing.
- `website_https.yml`: Ansible playbook for setting up HTTPS website. Migration consideration: Already in Ansible format, can be kept as-is.
- `poodle_fix.yml`: Ansible playbook for fixing SSL vulnerabilities. Migration consideration: Already in Ansible format, can be kept as-is.
- `index.html`: Static HTML file. Migration consideration: No changes needed.

### Target Details

Based on the source configuration files:

- **Operating System**: Ubuntu 20.04 (explicitly specified in kitchen.yml)
- **Virtual Machine Technology**: Vagrant (specified in kitchen.yml driver)
- **Cloud Platform**: Not specified, appears to be on-premises or generic cloud VM deployment

## Migration Approach

### Key Dependencies to Address

- **Chef InSpec (latest)**: Replace with Ansible-native solutions:
  - For compliance testing: Use Ansible Lint, OpenSCAP with Ansible, or Ansible's assert module
  - For infrastructure validation: Use Ansible's uri module and assert module
  - For SSL/TLS validation: Use Ansible's openssl_certificate_info module with assert

- **Chef Automate/Infra Server**: Replace with:
  - Ansible AWX/Tower for web UI and job scheduling
  - Ansible Collections for configuration management
  - Ansible Vault for secrets management

### Security Considerations

- **SSH Configuration Testing**: Migrate the SSH profile tests to Ansible assertions or OpenSCAP checks
  - Migration approach: Create Ansible tasks that check SSH configuration parameters and assert correct values
  
- **SSL/TLS Protocol Verification**: Ensure proper TLS protocols are enabled and insecure ones disabled
  - Migration approach: Use Ansible's openssl_certificate_info module to verify certificate properties
  
- **Vault/secrets management**:
  - Hardcoded credentials in setup scripts (username, password) should be moved to Ansible Vault
  - SSL certificates and keys should be managed securely using Ansible Vault or external secret management
  - Count of credentials detected: 5 (username, longusername, useremail, userpassword, orgname)

### Technical Challenges

- **InSpec Test Conversion**: Converting InSpec's domain-specific language to Ansible assertions
  - Mitigation: Create reusable Ansible roles that implement similar compliance checks
  
- **Validation Logic**: Replicating InSpec's validation capabilities in Ansible
  - Mitigation: Combine Ansible's uri module with assert module to create similar validation workflows

### Migration Order

1. **Ansible Playbooks** (website_https.yml, poodle_fix.yml): Already in Ansible format, no migration needed
2. **InSpec Tests** (website_https_verify.rb, ssh_profile.rb): Convert to Ansible assertions or dedicated compliance roles
3. **Chef Server Deployment Scripts** (deploy-automate.sh, deploy-chef-server.sh): Convert to Ansible roles for infrastructure setup

### Assumptions

1. The primary purpose of this repository is to demonstrate Chef InSpec with Ansible rather than being a production deployment
2. The Chef InSpec tests are used for validation only and not for remediation
3. The hardcoded credentials in the deployment scripts are examples and not used in production
4. The self-signed certificates in the Ansible playbooks are for demonstration purposes only
5. There are no external dependencies or integrations beyond what's visible in the repository
6. The target environment is Ubuntu 20.04 running on Vagrant VMs
7. There are no custom Chef resources or complex Chef-specific logic that would require special handling
8. The migration is primarily focused on replacing Chef InSpec tests with Ansible-native solutions
9. The existing Ansible playbooks can be retained with minimal modifications