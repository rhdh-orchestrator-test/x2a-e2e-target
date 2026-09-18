# MIGRATION FROM CHEF INSPEC TO ANSIBLE

This repository contains demonstration examples for using Chef InSpec alongside Ansible for compliance automation, rather than traditional Chef cookbooks. The migration scope is limited as the repository primarily contains Ansible playbooks with InSpec test verification, plus Chef server deployment scripts. The migration complexity is **LOW** with an estimated timeline of **1-2 weeks** for full conversion to native Ansible testing approaches.

## Module Migration Plan

This repository contains hybrid Chef/Ansible demonstration content that needs individual migration planning:

### MODULE INVENTORY

**website-https-demo**:
- Description: Ansible playbook demonstrating HTTPS website deployment with Apache SSL configuration, self-signed certificate generation, and virtual host setup
- Path: chef-and-ansible/website_https.yml
- Technology: Ansible (already migrated)
- Key Features: Apache 2.4.41 installation, OpenSSL certificate generation, SSL virtual host configuration, directory structure creation

**poodle-ssl-fix**:
- Description: Ansible playbook for SSL security hardening by disabling SSLv3 and enforcing TLS 1.2 to mitigate POODLE vulnerability
- Path: chef-and-ansible/poodle_fix.yml
- Technology: Ansible (already migrated)
- Key Features: Apache SSL protocol configuration, regex-based configuration replacement, service restart handling

**inspec-website-verification**:
- Description: Chef InSpec compliance tests for HTTPS website functionality and SSL security validation
- Path: chef-and-ansible/tests/website_https_verify.rb
- Technology: Chef InSpec
- Key Features: Port 443 listening verification, HTTPS response validation, SSL protocol compliance checks

**inspec-ssh-security**:
- Description: Chef InSpec security compliance test for SSH root login restrictions following STIG guidelines
- Path: chef-and-ansible/tests/ssh_profile.rb
- Technology: Chef InSpec
- Key Features: SSH configuration validation, STIG compliance (RHEL-08-000227), root login prevention verification

### Infrastructure Files

- `kitchen.yml`: Test Kitchen configuration for running Ansible playbooks with InSpec verification - needs conversion to molecule or native Ansible testing
- `deploy-automate.sh`: Chef Automate and Infra Server deployment script - can be converted to Ansible playbook for infrastructure provisioning
- `deploy-chef-server.sh`: Standalone Chef Infra Server deployment script - can be converted to Ansible playbook
- `index.html`: Static test content for web server validation - no migration needed

### Target Details

- **Operating System**: Ubuntu 20.04 LTS (specified in kitchen.yml platform configuration)
- **Virtual Machine Technology**: Vagrant with VirtualBox (inferred from Test Kitchen driver configuration)
- **Cloud Platform**: Not specified - designed for local development and testing environments

## Migration Approach

### Key Dependencies to Address
- **Chef InSpec**: Replace with Ansible native testing modules (uri, assert, service_facts) or molecule with testinfra
- **Test Kitchen**: Replace with molecule for Ansible playbook testing and verification
- **Chef Automate/Server**: Convert deployment scripts to Ansible playbooks using package management and service modules

### Security Considerations
- SSL/TLS certificate management: Current implementation uses self-signed certificates - migration should consider proper certificate authority integration
- SSH security validation: InSpec SSH tests need conversion to Ansible assert tasks or custom validation modules
- STIG compliance verification: Current InSpec controls need mapping to Ansible security hardening roles or custom compliance tasks
- Credential management: Deployment scripts contain hardcoded passwords that should be moved to Ansible Vault

### Technical Challenges
- **InSpec to Ansible Testing**: Converting Chef InSpec compliance tests to native Ansible testing requires rewriting test logic using Ansible's assert, uri, and service_facts modules
- **Test Kitchen Replacement**: Migration from Test Kitchen to molecule requires restructuring test scenarios and verification approaches
- **Compliance Framework**: Loss of InSpec's rich compliance reporting may require integration with external compliance tools or custom reporting solutions

### Migration Order
1. **Infrastructure Deployment Scripts** (setup-automate/) - Convert bash scripts to Ansible playbooks for Chef server provisioning
2. **Ansible Playbook Testing** (chef-and-ansible/kitchen.yml) - Replace Test Kitchen with molecule for playbook testing
3. **Compliance Test Migration** (chef-and-ansible/tests/) - Convert InSpec tests to Ansible native testing or integrate with alternative compliance tools

### Assumptions
- The target environment will continue using Ubuntu 20.04 or migrate to a newer LTS version
- Ansible molecule will be acceptable as a replacement for Test Kitchen testing workflows
- Native Ansible testing capabilities (assert, uri modules) will be sufficient for basic compliance validation
- More complex compliance requirements may need integration with external tools like OpenSCAP or custom Ansible modules
- The demonstration nature of this repository suggests full enterprise compliance features may not be required
- SSL certificate management will be enhanced beyond self-signed certificates in production environments
- Hardcoded credentials in deployment scripts indicate this is a development/demo environment that will need proper secret management in production